"""
File Watcher Module for Data Pipeline

Provides file system monitoring to detect new CSV exports
from Epicor for automatic import processing.
"""

from .file_watcher import (
    FileWatcher,
    FileWatcherEvent,
    FileWatcherCallback,
)

__all__ = [
    "FileWatcher",
    "FileWatcherEvent",
    "FileWatcherCallback",
]
