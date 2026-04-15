"""check_script_status - Verify script execution status via log correlation."""

from enum import Enum
import os
import re
from pathlib import Path
from typing import List, Tuple


class LogStatus(Enum):
    """Log severity levels for script status checks."""

    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


def check_script_status(script_path: str, trace_id: str) -> LogStatus:
    """
    Check log status for a script run with given trace_id.

    Searches _clog/ directory next to script for log files
    containing lines with | cmon_trace=<trace_id>.

    Returns LogStatus based on highest severity found:
    - ERROR: found ERROR level log
    - WARNING: found WARN level (no ERROR)
    - SUCCESS: INFO/SUCCESS only

    Raises ValueError if no logs found with matching trace_id.

    Args:
        script_path: Path to the script that was executed
        trace_id: The cmon_trace identifier to search for

    Returns:
        LogStatus enum value indicating the highest severity found
    """
    script_path = Path(script_path)
    clog_dir = script_path.parent / "_clog"

    if not clog_dir.exists():
        raise ValueError(f"No _clog directory found at {clog_dir.parent}")

    # Pattern to match trace_id in log lines
    trace_pattern = re.compile(rf"\| cmon_trace={re.escape(trace_id)}$")

    # Track highest severity found
    highest_status = None
    found_any = False

    # Check all log files in _clog directory
    for log_file in clog_dir.glob("*.log"):
        status = _check_log_file(log_file, trace_pattern)
        if status is not None:
            found_any = True
            if status == LogStatus.ERROR:
                highest_status = LogStatus.ERROR
                break  # Can't get worse than ERROR
            elif status == LogStatus.WARNING:
                if highest_status != LogStatus.ERROR:
                    highest_status = LogStatus.WARNING
            elif highest_status is None:
                highest_status = LogStatus.SUCCESS

    if not found_any:
        raise ValueError(f"No logs found with trace_id={trace_id}")

    return highest_status if highest_status else LogStatus.SUCCESS


def _check_log_file(log_file: Path, trace_pattern: re.Pattern) -> LogStatus | None:
    """
    Check a single log file for trace_id and return highest severity.

    Returns None if trace_id not found in this file.
    """
    highest_status = None

    try:
        with open(log_file, "r") as f:
            for line in f:
                if trace_pattern.search(line):
                    # Parse log level from line
                    # Format: YYYY-MM-DD HH:mm:ss | LEVEL | ...
                    status = _parse_log_level(line)
                    if status == LogStatus.ERROR:
                        return LogStatus.ERROR
                    elif (
                        status == LogStatus.WARNING
                        and highest_status != LogStatus.ERROR
                    ):
                        highest_status = LogStatus.WARNING
                    elif highest_status is None:
                        highest_status = status
    except (IOError, OSError):
        pass

    return highest_status


def _parse_log_level(line: str) -> LogStatus:
    """Parse log level from a log line."""
    # Log format: YYYY-MM-DD HH:mm:ss | LEVEL | module:func:line | user | message
    parts = line.split("|")
    if len(parts) >= 2:
        level_str = parts[1].strip()
        if level_str == "ERROR":
            return LogStatus.ERROR
        elif level_str == "WARN":
            return LogStatus.WARNING
    return LogStatus.SUCCESS


__all__ = ["LogStatus", "check_script_status"]
