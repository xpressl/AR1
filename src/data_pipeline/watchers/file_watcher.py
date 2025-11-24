"""
File Watcher Service

Monitors the CSV import directory for new or modified files.
Triggers callbacks when new Epicor exports are detected.

Features:
- Monitor directory for new CSV files
- Debounce rapid changes (wait for file write to complete)
- Handle file locks and partial writes
- Configurable file patterns
- Event callbacks for processing
"""

import os
import time
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
import logging
import threading
from queue import Queue, Empty

try:
    from watchdog.observers import Observer
    from watchdog.events import (
        FileSystemEventHandler,
        FileCreatedEvent,
        FileModifiedEvent,
        FileMovedEvent,
        FileSystemEvent,
    )
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object

from ..config.epicor_config import EpicorConfig

logger = logging.getLogger(__name__)


class FileEventType(Enum):
    """Types of file system events."""
    CREATED = "created"
    MODIFIED = "modified"
    MOVED = "moved"


@dataclass
class FileWatcherEvent:
    """Event generated when a file change is detected."""
    event_type: FileEventType
    file_path: Path
    file_name: str
    timestamp: datetime
    file_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "event_type": self.event_type.value,
            "file_path": str(self.file_path),
            "file_name": self.file_name,
            "timestamp": self.timestamp.isoformat() + "Z",
            "file_size": self.file_size,
            "metadata": self.metadata,
        }


# Type alias for callback functions
FileWatcherCallback = Callable[[FileWatcherEvent], None]


class CSVFileHandler(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    """
    Custom file event handler for CSV files.

    Filters events to only CSV files matching the expected
    Epicor export patterns.
    """

    # Expected CSV file names from Epicor
    EXPECTED_FILES = {
        "CustomerMaster.csv",
        "OpenAR.csv",
        "Payments.csv",
        "CreditStatus.csv",
    }

    def __init__(
        self,
        event_queue: Queue,
        file_patterns: Optional[Set[str]] = None,
        debounce_delay: float = 5.0,
    ):
        """
        Initialize the CSV file handler.

        Args:
            event_queue: Queue to put events for processing
            file_patterns: Set of file patterns to watch (default: Epicor files)
            debounce_delay: Seconds to wait for file writes to complete
        """
        if WATCHDOG_AVAILABLE:
            super().__init__()

        self.event_queue = event_queue
        self.file_patterns = file_patterns or self.EXPECTED_FILES
        self.debounce_delay = debounce_delay

        # Track recent events for debouncing
        self._pending_events: Dict[str, datetime] = {}
        self._lock = threading.Lock()

    def _should_process(self, path: str) -> bool:
        """Check if the file path should be processed."""
        file_name = Path(path).name

        # Check exact match
        if file_name in self.file_patterns:
            return True

        # Check if it's a CSV file (case insensitive)
        if file_name.lower().endswith('.csv'):
            # Accept any CSV if patterns not strictly enforced
            return True

        return False

    def _is_debounced(self, path: str) -> bool:
        """Check if event is within debounce window."""
        with self._lock:
            last_event = self._pending_events.get(path)
            now = datetime.now()

            if last_event:
                elapsed = (now - last_event).total_seconds()
                if elapsed < self.debounce_delay:
                    return True

            self._pending_events[path] = now
            return False

    def _create_event(
        self,
        event_type: FileEventType,
        src_path: str,
    ) -> Optional[FileWatcherEvent]:
        """Create a FileWatcherEvent from a file system event."""
        try:
            path = Path(src_path)

            # Wait for file to be fully written
            if not self._wait_for_file_ready(path):
                logger.warning(f"File not ready after waiting: {path}")
                return None

            file_size = path.stat().st_size if path.exists() else 0

            return FileWatcherEvent(
                event_type=event_type,
                file_path=path,
                file_name=path.name,
                timestamp=datetime.utcnow(),
                file_size=file_size,
                metadata={
                    "modified_time": datetime.fromtimestamp(
                        path.stat().st_mtime
                    ).isoformat() if path.exists() else None,
                },
            )
        except Exception as e:
            logger.error(f"Error creating file event: {e}")
            return None

    def _wait_for_file_ready(
        self,
        path: Path,
        max_wait: float = 30.0,
        check_interval: float = 0.5,
    ) -> bool:
        """
        Wait for file to be fully written (not locked).

        Args:
            path: Path to the file
            max_wait: Maximum seconds to wait
            check_interval: Seconds between checks

        Returns:
            True if file is ready, False if timeout
        """
        start_time = time.time()
        last_size = -1

        while time.time() - start_time < max_wait:
            try:
                if not path.exists():
                    time.sleep(check_interval)
                    continue

                current_size = path.stat().st_size

                # Check if size is stable
                if current_size == last_size and current_size > 0:
                    # Try to open file to verify it's not locked
                    try:
                        with open(path, 'rb') as f:
                            f.read(1)
                        return True
                    except (IOError, OSError):
                        pass

                last_size = current_size
                time.sleep(check_interval)

            except OSError:
                time.sleep(check_interval)

        return False

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file created event."""
        if event.is_directory:
            return

        if not self._should_process(event.src_path):
            return

        if self._is_debounced(event.src_path):
            logger.debug(f"Debounced create event: {event.src_path}")
            return

        logger.info(f"File created: {event.src_path}")
        file_event = self._create_event(FileEventType.CREATED, event.src_path)
        if file_event:
            self.event_queue.put(file_event)

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modified event."""
        if event.is_directory:
            return

        if not self._should_process(event.src_path):
            return

        if self._is_debounced(event.src_path):
            logger.debug(f"Debounced modify event: {event.src_path}")
            return

        logger.info(f"File modified: {event.src_path}")
        file_event = self._create_event(FileEventType.MODIFIED, event.src_path)
        if file_event:
            self.event_queue.put(file_event)

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file moved event (renamed)."""
        if event.is_directory:
            return

        dest_path = getattr(event, 'dest_path', None)
        if not dest_path:
            return

        if not self._should_process(dest_path):
            return

        if self._is_debounced(dest_path):
            logger.debug(f"Debounced move event: {dest_path}")
            return

        logger.info(f"File moved: {event.src_path} -> {dest_path}")
        file_event = self._create_event(FileEventType.MOVED, dest_path)
        if file_event:
            file_event.metadata["source_path"] = event.src_path
            self.event_queue.put(file_event)


class FileWatcher:
    """
    File system watcher for Epicor CSV exports.

    Monitors the configured import directory and triggers
    callbacks when new or modified CSV files are detected.

    Usage:
        watcher = FileWatcher(config)
        watcher.add_callback(my_callback_function)
        watcher.start()
        ...
        watcher.stop()

    The callback function receives a FileWatcherEvent object
    containing details about the changed file.
    """

    def __init__(
        self,
        config: Optional[EpicorConfig] = None,
        watch_path: Optional[str] = None,
    ):
        """
        Initialize the file watcher.

        Args:
            config: Optional EpicorConfig for settings
            watch_path: Override path to watch (default from config)
        """
        if not WATCHDOG_AVAILABLE:
            logger.warning(
                "watchdog library not installed. "
                "File watching will use polling fallback."
            )

        self.config = config or EpicorConfig()
        self.watch_path = Path(watch_path or self.config.csv_import_path)
        self.debounce_delay = self.config.watch_debounce_delay

        self._callbacks: List[FileWatcherCallback] = []
        self._event_queue: Queue = Queue()
        self._running = False
        self._observer = None
        self._processor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Stats tracking
        self._stats = {
            "events_processed": 0,
            "errors": 0,
            "last_event_time": None,
            "start_time": None,
        }

    def add_callback(self, callback: FileWatcherCallback) -> None:
        """
        Add a callback to be invoked when files change.

        Args:
            callback: Function that takes a FileWatcherEvent
        """
        self._callbacks.append(callback)
        logger.debug(f"Added file watcher callback: {callback.__name__}")

    def remove_callback(self, callback: FileWatcherCallback) -> None:
        """
        Remove a previously added callback.

        Args:
            callback: The callback function to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def start(self) -> None:
        """
        Start watching for file changes.

        Creates an observer thread for file system events
        and a processor thread for handling callbacks.
        """
        if self._running:
            logger.warning("File watcher already running")
            return

        # Verify watch path exists
        if not self.watch_path.exists():
            logger.error(f"Watch path does not exist: {self.watch_path}")
            raise FileNotFoundError(f"Watch path not found: {self.watch_path}")

        self._running = True
        self._stop_event.clear()
        self._stats["start_time"] = datetime.utcnow()

        if WATCHDOG_AVAILABLE:
            self._start_watchdog()
        else:
            self._start_polling()

        # Start event processor thread
        self._processor_thread = threading.Thread(
            target=self._process_events,
            daemon=True,
            name="FileEventProcessor",
        )
        self._processor_thread.start()

        logger.info(f"Started file watcher on: {self.watch_path}")

    def _start_watchdog(self) -> None:
        """Start the watchdog observer."""
        handler = CSVFileHandler(
            event_queue=self._event_queue,
            debounce_delay=self.debounce_delay,
        )

        self._observer = Observer()
        self._observer.schedule(handler, str(self.watch_path), recursive=False)
        self._observer.start()

    def _start_polling(self) -> None:
        """Start polling-based file watching (fallback)."""
        polling_thread = threading.Thread(
            target=self._polling_loop,
            daemon=True,
            name="FilePolling",
        )
        polling_thread.start()

    def _polling_loop(self) -> None:
        """Polling loop for systems without watchdog."""
        known_files: Dict[str, float] = {}  # path -> mtime

        poll_interval = self.config.watch_poll_interval

        while not self._stop_event.is_set():
            try:
                current_files = {}

                for file_path in self.watch_path.glob("*.csv"):
                    mtime = file_path.stat().st_mtime
                    current_files[str(file_path)] = mtime

                    if str(file_path) not in known_files:
                        # New file
                        event = FileWatcherEvent(
                            event_type=FileEventType.CREATED,
                            file_path=file_path,
                            file_name=file_path.name,
                            timestamp=datetime.utcnow(),
                            file_size=file_path.stat().st_size,
                        )
                        self._event_queue.put(event)

                    elif known_files[str(file_path)] != mtime:
                        # Modified file
                        event = FileWatcherEvent(
                            event_type=FileEventType.MODIFIED,
                            file_path=file_path,
                            file_name=file_path.name,
                            timestamp=datetime.utcnow(),
                            file_size=file_path.stat().st_size,
                        )
                        self._event_queue.put(event)

                known_files = current_files

            except Exception as e:
                logger.error(f"Polling error: {e}")

            self._stop_event.wait(timeout=poll_interval)

    def _process_events(self) -> None:
        """Process events from the queue and invoke callbacks."""
        while not self._stop_event.is_set():
            try:
                # Wait for event with timeout
                event = self._event_queue.get(timeout=1.0)

                self._stats["events_processed"] += 1
                self._stats["last_event_time"] = datetime.utcnow()

                logger.info(
                    f"Processing file event: {event.event_type.value} - {event.file_name}"
                )

                # Invoke all callbacks
                for callback in self._callbacks:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(
                            f"Error in file watcher callback: {e}",
                            exc_info=True,
                        )
                        self._stats["errors"] += 1

            except Empty:
                # No events, continue loop
                continue
            except Exception as e:
                logger.error(f"Error processing file event: {e}")
                self._stats["errors"] += 1

    def stop(self) -> None:
        """Stop watching for file changes."""
        if not self._running:
            return

        self._running = False
        self._stop_event.set()

        # Stop watchdog observer
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5.0)
            self._observer = None

        # Stop processor thread
        if self._processor_thread:
            self._processor_thread.join(timeout=5.0)
            self._processor_thread = None

        logger.info("Stopped file watcher")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get file watcher statistics.

        Returns:
            Dictionary with watcher statistics
        """
        stats = self._stats.copy()
        stats["running"] = self._running
        stats["watch_path"] = str(self.watch_path)
        stats["callbacks_registered"] = len(self._callbacks)
        stats["queue_size"] = self._event_queue.qsize()

        if stats["start_time"]:
            uptime = datetime.utcnow() - stats["start_time"]
            stats["uptime_seconds"] = uptime.total_seconds()
            stats["start_time"] = stats["start_time"].isoformat() + "Z"

        if stats["last_event_time"]:
            stats["last_event_time"] = stats["last_event_time"].isoformat() + "Z"

        return stats

    @property
    def is_running(self) -> bool:
        """Check if the watcher is currently running."""
        return self._running

    def __enter__(self):
        """Context manager entry - start watching."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop watching."""
        self.stop()
        return False


def create_import_trigger_callback(
    import_function: Callable[[Path], None],
) -> FileWatcherCallback:
    """
    Create a callback that triggers an import function.

    Utility function to create a properly typed callback
    from an import function.

    Args:
        import_function: Function that takes a file path to import

    Returns:
        FileWatcherCallback that invokes the import function
    """
    def callback(event: FileWatcherEvent) -> None:
        logger.info(f"Triggering import for: {event.file_name}")
        try:
            import_function(event.file_path)
        except Exception as e:
            logger.error(f"Import failed for {event.file_name}: {e}")

    return callback
