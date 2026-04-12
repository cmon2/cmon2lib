"""
Centralized logging for cmon2lib.

Dual-output logging:
- Console (terminal): Just the message with color. WARNING/ERROR show level prefix.
- File: Full format with timestamp, level, module, user, message.

Console format: <message> (with color)
Console format for WARNING/ERROR: WARN: <message> or ERR: <message>

File format: YYYY-MM-DD HH:mm:ss | LEVEL    | module:func:line | USER | message

Features:
- Auto-init on first clog() call
- File logging to _clog/ directory
- Archive log (rotated by time)
- Summary log (INFO, SUCCESS, ERROR only)
- WARN/ERROR archive renaming
- Age-based cleanup (archives older than 30 days deleted, except _WARN/_ERR/_csummary)
- Exception formatting (single-line)
"""

import os
import sys
import time
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta
from typing import Optional

# Global state
_clog_initialized = False
_clog_dir = None
_clog_archive = None
_clog_summary = None
_clog_archive_renamed = False


def _get_user() -> str:
    """Get the current OS user."""
    return os.getenv("USER") or os.getenv("USERNAME") or "unknown"


def _get_module_name() -> str:
    """Get the module name from the call stack."""
    # Skip: _get_module_name -> _clog -> clog (3 frames)
    # Return the actual caller
    frame = sys._getframe(3)
    module = frame.f_globals.get("__name__", "__main__")
    # Get just the last component for brevity
    return module.split(".")[-1] if module else "unknown"


def _get_caller_info() -> tuple:
    """Get caller file, function, line from the call stack."""
    # Skip: _get_caller_info -> _clog -> clog -> actual caller (4 frames)
    frame = sys._getframe(4)
    name = frame.f_globals.get("__name__", "__main__")
    func = frame.f_code.co_name
    line = frame.f_lineno
    module = name.split(".")[-1] if name else "unknown"
    return module, func, line


def _get_log_dir() -> Path:
    """Get the _clog directory for the calling module."""
    # Get the directory of the calling module
    frame = sys._getframe(3)
    module_file = frame.f_code.co_filename
    module_dir = Path(module_file).parent
    log_dir = module_dir / "_clog"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Ensure .gitignore exists
    gitignore = log_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("""# Ignore clog archive logs (they start with 20XX for the year)
*.log

# Ignore clog summary logs
*_csummary.log

# Explicitly track WARN and ERR logs (overrides the 20*.log ignore)
!*_WARN.log
!*_ERR.log
""")
    return log_dir


def _get_archive_name(module_name: str) -> Path:
    """Generate archive log filename with timestamp."""
    log_dir = _get_log_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return log_dir / f"{timestamp}_{module_name}.log"


def _get_summary_name(module_name: str) -> Path:
    """Generate summary log filename."""
    log_dir = _get_log_dir()
    return log_dir / f"{module_name}_csummary.log"


def _cleanup_old_archives(log_dir: Path, max_age_days: int = 30):
    """
    Delete archive log files older than max_age_days.

    Protected files (never deleted):
    - *_WARN.log
    - *_ERR.log
    - *_csummary.log
    """
    if not log_dir.exists():
        return

    cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
    protected_patterns = ("_WARN.log", "_ERR.log", "_csummary.log")

    for log_file in log_dir.glob("*.log"):
        # Skip protected files
        if log_file.name.endswith(protected_patterns):
            continue

        # Skip current archive (might still be open)
        if _clog_archive and log_file == _clog_archive:
            continue

        # Check file age by mtime
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
            except OSError:
                pass  # Skip if can't delete (e.g., permissions)


def _format_log_record(record: dict) -> str:
    """Custom format function that includes USER from extra (for file logging)."""
    timestamp = record["time"].strftime("%Y-%m-%d %H:%M:%S")
    level = record["level"].name.ljust(8)
    name = record["name"]
    function = record["function"]
    line = record["line"]
    user = record["extra"].get("user", "unknown")
    message = record["message"]
    return f"{timestamp} | {level} | {name}:{function}:{line} | {user} | {message}"


def _format_console(record: dict) -> str:
    """
    Console format: message only with color.
    WARNING/ERROR get a level prefix.
    """
    level = record["level"].name
    message = record["message"]

    if level == "WARNING":
        return f"<yellow>WARN:</yellow> {message}"
    elif level == "ERROR":
        return f"<red>ERR:</red> {message}"
    elif level == "SUCCESS":
        return f"<green>{message}</green>"
    elif level == "INFO":
        return message
    elif level == "DEBUG":
        return f"<dim>{message}</dim>"
    elif level == "TRACE":
        return f"<dim>{message}</dim>"
    else:
        return message


def _init_clog():
    """Initialize logging. Called automatically on first clog() call."""
    global _clog_initialized, _clog_dir, _clog_archive, _clog_summary

    if _clog_initialized:
        return

    module_name = _get_module_name()
    _clog_dir = _get_log_dir()
    _clog_archive = _get_archive_name(module_name)
    _clog_summary = _get_summary_name(module_name)

    # Cleanup old archives (older than 30 days, except _WARN/_ERR/_csummary)
    _cleanup_old_archives(_clog_dir)

    # Create archive file
    _clog_archive.touch()

    # Remove default loguru handler
    logger.remove()

    # Console output - message only with color, WARN/ERR prefixed
    logger.add(
        sys.stderr,
        format=_format_console,
        colorize=True,
        level="DEBUG",
    )

    # File handler for archive - full metadata format
    logger.add(
        _clog_archive,
        format=_format_log_record,
        level="DEBUG",
        rotation=False,
        retention=None,
        compression=None,
    )

    _clog_initialized = True


def _clog(level: str, msg: str, *args, exception: Optional[Exception] = None):
    """
    Central logging gateway for cmon2lib.

    Args:
        level: Log level (trace, debug, info, success, warning, error, critical)
        msg: Log message (supports {} formatting)
        *args: Format arguments for msg
        exception: Optional exception to include in message
    """
    global _clog_initialized, _clog_archive, _clog_summary, _clog_archive_renamed

    # Auto-init on first call
    if not _clog_initialized:
        _init_clog()

    # Build message with exception if provided
    if exception is not None:
        msg = f"{msg}: {type(exception).__name__}: {exception}"

    # Format message if args provided
    if args:
        msg = msg.format(*args)

    # Uppercase level for consistency
    level_upper = level.upper()

    # Validate level
    valid_levels = {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}
    if level_upper not in valid_levels:
        logger.warning(f"Invalid log level '{level}', defaulting to INFO: {msg}")
        level_upper = "INFO"

    # Log with depth=3 to skip _clog wrapper frames, bind user to extra
    logger.bind(user=_get_user()).opt(depth=3).log(level_upper, msg)

    # Handle summary log and archive renaming for WARN/ERROR
    if level_upper in {"INFO", "SUCCESS", "ERROR"}:
        if _clog_summary and _clog_summary.exists():
            _write_to_summary(level_upper, msg)

    # Rename archive if WARN or ERROR
    if level_upper in {"WARNING", "ERROR"} and not _clog_archive_renamed:
        _rename_archive(level_upper)


def _write_to_summary(level: str, msg: str):
    """Write INFO, SUCCESS, or ERROR messages to summary log."""
    if _clog_summary:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Get caller info for summary
        module, func, line = _get_caller_info()
        user = _get_user()
        level_padded = f"{level: <8}"
        summary_line = (
            f"{timestamp} | {level_padded} | {module}:{func}:{line} | {user} | {msg}\n"
        )
        with open(_clog_summary, "a") as f:
            f.write(summary_line)


def _rename_archive(level: str):
    """Rename archive to include WARN or ERR suffix."""
    global _clog_archive, _clog_archive_renamed

    if _clog_archive and _clog_archive.exists() and not _clog_archive_renamed:
        suffix = "WARN" if level == "WARNING" else "ERR"
        new_archive = _clog_archive.parent / f"{_clog_archive.stem}_{suffix}.log"
        _clog_archive.rename(new_archive)
        _clog_archive = new_archive
        _clog_archive_renamed = True


def clog(level: str, msg: str, *args, exception: Optional[Exception] = None):
    """
    Central logging gateway for cmon2lib.

    Usage:
        clog('info', 'message')
        clog('debug', 'value: {}', 42)
        clog('error', 'Connection failed', exception=e)

    Args:
        level: Log level (trace, debug, info, success, warning, error, critical)
        msg: Log message (supports {} formatting)
        *args: Format arguments for msg
        exception: Optional Exception to include in message (format: "msg: ExceptionType: message")
    """
    _clog(level, msg, *args, exception=exception)
