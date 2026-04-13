"""
Central logging for cmon2lib (clog).

Dual-output logging:
- Console (terminal): Just the message with color. WARNING/ERROR show level prefix.
- File: Full format with timestamp, level, module, user, message.

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
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger

from .lib import get_user, get_module_name, get_caller_info
from .lib import format_log_record, format_console


# =============================================================================
# GLOBAL STATE
# =============================================================================

_clog_initialized = False
_clog_dir = None
_clog_archive = None
_clog_summary = None
_clog_archive_renamed = False
_custom_log_dir = None  # Optional custom log directory path


# =============================================================================
# INIT FUNCTION
# =============================================================================


def init_clog(log_dir: Optional[str] = None):
    """
    Initialize clog with a custom log directory.

    Args:
        log_dir: Optional path to directory for _clog/ logs.
                 If not provided, logs are written next to the calling script.
    """
    global _clog_initialized, _custom_log_dir

    if log_dir is not None:
        _custom_log_dir = Path(log_dir)
        _clog_initialized = False  # Force re-init with new directory


# =============================================================================
# LOG DIR & ARCHIVE HELPERS
# =============================================================================


def _get_log_dir() -> Path:
    """Get the _clog directory for the calling module."""
    # Use custom log directory if set, otherwise derive from caller
    if _custom_log_dir is not None:
        log_dir = _custom_log_dir / "_clog"
        log_dir.mkdir(parents=True, exist_ok=True)
        _ensure_gitignore(log_dir)
        return log_dir

    # Walk up frames to find the actual user script (skip cmon2lib internals)
    # Frame 0 = _get_log_dir, 1 = _init_clog, 2 = _clog, 3 = clog (if direct), 4+ = user script
    for depth in range(2, 10):
        try:
            frame = sys._getframe(depth)
            module_file = frame.f_code.co_filename
            # Skip if inside cmon2lib package
            if "cmon2lib" in Path(module_file).parts:
                continue
            # Found a frame outside cmon2lib
            module_dir = Path(module_file).parent
            log_dir = module_dir / "_clog"
            log_dir.mkdir(parents=True, exist_ok=True)
            _ensure_gitignore(log_dir)
            return log_dir
        except ValueError:
            break

    # Fallback: use module where clog was called from
    frame = sys._getframe(3)
    module_file = frame.f_code.co_filename
    module_dir = Path(module_file).parent
    log_dir = module_dir / "_clog"
    log_dir.mkdir(parents=True, exist_ok=True)
    _ensure_gitignore(log_dir)
    return log_dir


def _ensure_gitignore(log_dir: Path):
    """Ensure .gitignore exists in log directory."""
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


def _get_archive_name(module_name: str) -> Path:
    """Generate archive log filename with timestamp."""
    log_dir = _get_log_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return log_dir / f"{timestamp}_{module_name}.log"


def _get_summary_name(module_name: str) -> Path:
    """Generate summary log filename."""
    log_dir = _get_log_dir()
    return log_dir / f"{module_name}_csummary.log"


# =============================================================================
# CLEANUP
# =============================================================================


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
        if log_file.name.endswith(protected_patterns):
            continue
        if _clog_archive and log_file == _clog_archive:
            continue
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
            except OSError:
                pass  # Skip if can't delete


# =============================================================================
# SUMMARY & ARCHIVE
# =============================================================================


def _write_to_summary(level: str, msg: str):
    """Write INFO, SUCCESS, or ERROR messages to summary log."""
    if _clog_summary:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        module, func, line = get_caller_info()
        user = get_user()
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


# =============================================================================
# INIT & LOG
# =============================================================================


def _init_clog():
    """Initialize logging. Called automatically on first clog() call."""
    global _clog_initialized, _clog_dir, _clog_archive, _clog_summary

    if _clog_initialized:
        return

    module_name = get_module_name()
    _clog_dir = _get_log_dir()
    _clog_archive = _get_archive_name(module_name)
    _clog_summary = _get_summary_name(module_name)

    _cleanup_old_archives(_clog_dir)
    _clog_archive.touch()

    logger.remove()

    # Console: minimal format with color, WARN/ERR prefixed
    logger.add(
        sys.stderr,
        format=format_console,
        colorize=True,
        level="DEBUG",
    )

    # File: full metadata format
    logger.add(
        _clog_archive,
        format=format_log_record,
        level="DEBUG",
        rotation=False,
        retention=None,
        compression=None,
    )

    _clog_initialized = True


def _clog(level: str, msg: str, *args, exception: Optional[Exception] = None):
    """
    Internal logging gateway.

    Args:
        level: Log level (trace, debug, info, success, warning, error, critical)
        msg: Log message (supports {} formatting)
        *args: Format arguments for msg
        exception: Optional exception to include in message
    """
    global _clog_initialized, _clog_archive, _clog_summary, _clog_archive_renamed

    if not _clog_initialized:
        _init_clog()

    if exception is not None:
        msg = f"{msg}: {type(exception).__name__}: {exception}"

    if args:
        msg = msg.format(*args)

    level_upper = level.upper()

    valid_levels = {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}
    if level_upper not in valid_levels:
        logger.warning(f"Invalid log level '{level}', defaulting to INFO: {msg}")
        level_upper = "INFO"

    logger.bind(user=get_user()).opt(depth=2).log(level_upper, msg)

    if level_upper in {"INFO", "SUCCESS", "ERROR"}:
        if _clog_summary and _clog_summary.exists():
            _write_to_summary(level_upper, msg)

    if level_upper in {"WARNING", "ERROR"} and not _clog_archive_renamed:
        _rename_archive(level_upper)


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
