"""
Connection Health Service

Provides centralized health monitoring for all data connectors.
Supports periodic health checks, alerting, and status aggregation.
"""

import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
import logging
import threading
import time

from ..connectors.base_connector import DataConnector
from ..config.epicor_config import EpicorConfig

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels for connectors and overall system."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    connector_name: str
    status: HealthStatus
    timestamp: datetime
    response_time_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "connector_name": self.connector_name,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat() + "Z",
            "response_time_ms": round(self.response_time_ms, 2),
            "details": self.details,
            "errors": self.errors,
        }


@dataclass
class SystemHealthReport:
    """Aggregated health report for the entire system."""
    overall_status: HealthStatus
    timestamp: datetime
    connectors: List[HealthCheckResult]
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "overall_status": self.overall_status.value,
            "timestamp": self.timestamp.isoformat() + "Z",
            "connectors": [c.to_dict() for c in self.connectors],
            "summary": self.summary,
        }


class ConnectionHealthService:
    """
    Centralized health monitoring service for data connectors.

    Features:
    - Register multiple connectors for monitoring
    - Periodic background health checks
    - Alert callbacks when health changes
    - Historical health data tracking
    - Aggregated system health reports

    Usage:
        service = ConnectionHealthService(config)
        service.register_connector("csv", csv_connector)
        service.register_connector("db", db_connector)

        # Manual check
        report = service.check_all()

        # Background monitoring
        service.start_monitoring()
        ...
        service.stop_monitoring()
    """

    def __init__(
        self,
        config: Optional[EpicorConfig] = None,
        check_interval: Optional[int] = None,
    ):
        """
        Initialize the health service.

        Args:
            config: Optional EpicorConfig for default settings
            check_interval: Override for health check interval in seconds
        """
        self.config = config or EpicorConfig()
        self.check_interval = check_interval or self.config.health_check_interval

        self._connectors: Dict[str, DataConnector] = {}
        self._history: Dict[str, List[HealthCheckResult]] = {}
        self._history_max_entries: int = 100
        self._callbacks: List[Callable[[HealthCheckResult], None]] = []
        self._status_change_callbacks: List[
            Callable[[str, HealthStatus, HealthStatus], None]
        ] = []

        self._monitoring: bool = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        self._last_known_status: Dict[str, HealthStatus] = {}

    def register_connector(
        self,
        name: str,
        connector: DataConnector,
    ) -> None:
        """
        Register a connector for health monitoring.

        Args:
            name: Unique name for this connector
            connector: DataConnector instance to monitor
        """
        self._connectors[name] = connector
        self._history[name] = []
        self._last_known_status[name] = HealthStatus.UNKNOWN
        logger.info(f"Registered connector for health monitoring: {name}")

    def unregister_connector(self, name: str) -> None:
        """
        Remove a connector from health monitoring.

        Args:
            name: Name of the connector to remove
        """
        if name in self._connectors:
            del self._connectors[name]
            del self._history[name]
            del self._last_known_status[name]
            logger.info(f"Unregistered connector: {name}")

    def add_health_callback(
        self,
        callback: Callable[[HealthCheckResult], None],
    ) -> None:
        """
        Add a callback to be invoked after each health check.

        Args:
            callback: Function that takes a HealthCheckResult
        """
        self._callbacks.append(callback)

    def add_status_change_callback(
        self,
        callback: Callable[[str, HealthStatus, HealthStatus], None],
    ) -> None:
        """
        Add a callback for status changes.

        Args:
            callback: Function(connector_name, old_status, new_status)
        """
        self._status_change_callbacks.append(callback)

    def check_connector(self, name: str) -> HealthCheckResult:
        """
        Perform a health check on a specific connector.

        Args:
            name: Name of the registered connector

        Returns:
            HealthCheckResult with check details

        Raises:
            KeyError: If connector name is not registered
        """
        if name not in self._connectors:
            raise KeyError(f"Connector not registered: {name}")

        connector = self._connectors[name]
        start_time = time.time()

        try:
            # Call the connector's health check
            health_response = connector.health_check()
            elapsed_ms = (time.time() - start_time) * 1000

            # Map status string to enum
            status_str = health_response.get("status", "unknown")
            status = HealthStatus(status_str) if status_str in [s.value for s in HealthStatus] else HealthStatus.UNKNOWN

            result = HealthCheckResult(
                connector_name=name,
                status=status,
                timestamp=datetime.utcnow(),
                response_time_ms=elapsed_ms,
                details=health_response.get("details", {}),
                errors=health_response.get("errors", []),
            )

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"Health check failed for {name}: {e}")

            result = HealthCheckResult(
                connector_name=name,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.utcnow(),
                response_time_ms=elapsed_ms,
                details={},
                errors=[str(e)],
            )

        # Store in history
        self._add_to_history(name, result)

        # Check for status change
        old_status = self._last_known_status.get(name, HealthStatus.UNKNOWN)
        if result.status != old_status:
            self._last_known_status[name] = result.status
            self._notify_status_change(name, old_status, result.status)

        # Invoke callbacks
        for callback in self._callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.error(f"Health callback error: {e}")

        return result

    def check_all(self) -> SystemHealthReport:
        """
        Perform health checks on all registered connectors.

        Returns:
            SystemHealthReport with aggregated results
        """
        results: List[HealthCheckResult] = []
        status_counts = {status: 0 for status in HealthStatus}

        for name in self._connectors:
            result = self.check_connector(name)
            results.append(result)
            status_counts[result.status] += 1

        # Determine overall status
        if status_counts[HealthStatus.UNHEALTHY] > 0:
            overall = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall = HealthStatus.DEGRADED
        elif status_counts[HealthStatus.HEALTHY] > 0:
            overall = HealthStatus.HEALTHY
        else:
            overall = HealthStatus.UNKNOWN

        # Calculate summary
        total_response_time = sum(r.response_time_ms for r in results)
        avg_response_time = total_response_time / len(results) if results else 0

        summary = {
            "total_connectors": len(self._connectors),
            "healthy_count": status_counts[HealthStatus.HEALTHY],
            "degraded_count": status_counts[HealthStatus.DEGRADED],
            "unhealthy_count": status_counts[HealthStatus.UNHEALTHY],
            "avg_response_time_ms": round(avg_response_time, 2),
        }

        report = SystemHealthReport(
            overall_status=overall,
            timestamp=datetime.utcnow(),
            connectors=results,
            summary=summary,
        )

        logger.info(
            f"System health check complete: {overall.value} "
            f"({status_counts[HealthStatus.HEALTHY]}/{len(results)} healthy)"
        )

        return report

    def get_history(
        self,
        connector_name: str,
        limit: int = 10,
    ) -> List[HealthCheckResult]:
        """
        Get recent health check history for a connector.

        Args:
            connector_name: Name of the connector
            limit: Maximum number of results to return

        Returns:
            List of recent HealthCheckResults, newest first
        """
        history = self._history.get(connector_name, [])
        return history[-limit:][::-1]  # Return newest first

    def get_uptime_percentage(
        self,
        connector_name: str,
        period_hours: int = 24,
    ) -> float:
        """
        Calculate uptime percentage over a time period.

        Args:
            connector_name: Name of the connector
            period_hours: Number of hours to analyze

        Returns:
            Uptime percentage (0.0 to 100.0)
        """
        history = self._history.get(connector_name, [])
        if not history:
            return 0.0

        cutoff = datetime.utcnow() - timedelta(hours=period_hours)
        relevant = [h for h in history if h.timestamp >= cutoff]

        if not relevant:
            return 0.0

        healthy_count = sum(
            1 for h in relevant if h.status == HealthStatus.HEALTHY
        )

        return (healthy_count / len(relevant)) * 100

    def start_monitoring(self) -> None:
        """Start background health monitoring."""
        if self._monitoring:
            logger.warning("Health monitoring already running")
            return

        self._monitoring = True
        self._stop_event.clear()

        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="HealthMonitor",
        )
        self._monitor_thread.start()
        logger.info(
            f"Started health monitoring (interval: {self.check_interval}s)"
        )

    def stop_monitoring(self) -> None:
        """Stop background health monitoring."""
        if not self._monitoring:
            return

        self._monitoring = False
        self._stop_event.set()

        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
            self._monitor_thread = None

        logger.info("Stopped health monitoring")

    def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while not self._stop_event.is_set():
            try:
                self.check_all()
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")

            # Wait for next check or stop signal
            self._stop_event.wait(timeout=self.check_interval)

    def _add_to_history(self, name: str, result: HealthCheckResult) -> None:
        """Add a result to history, maintaining max size."""
        if name not in self._history:
            self._history[name] = []

        self._history[name].append(result)

        # Trim if too long
        if len(self._history[name]) > self._history_max_entries:
            self._history[name] = self._history[name][-self._history_max_entries:]

    def _notify_status_change(
        self,
        name: str,
        old_status: HealthStatus,
        new_status: HealthStatus,
    ) -> None:
        """Notify callbacks of a status change."""
        logger.warning(
            f"Health status changed for {name}: "
            f"{old_status.value} -> {new_status.value}"
        )

        for callback in self._status_change_callbacks:
            try:
                callback(name, old_status, new_status)
            except Exception as e:
                logger.error(f"Status change callback error: {e}")

    @property
    def is_monitoring(self) -> bool:
        """Check if background monitoring is active."""
        return self._monitoring

    @property
    def registered_connectors(self) -> List[str]:
        """Get list of registered connector names."""
        return list(self._connectors.keys())
