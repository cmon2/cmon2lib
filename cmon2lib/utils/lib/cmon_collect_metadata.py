"""Collect caller metadata for logging."""

import os
import sys


def get_user() -> str:
    """Get the current OS user."""
    return os.getenv("USER") or os.getenv("USERNAME") or "unknown"


def get_module_name() -> str:
    """
    Get the calling module name from the call stack.

    Returns the module name of the actual caller (not this lib).
    """
    # Skip: get_module_name -> ... -> clog (2 frames minimum)
    frame = sys._getframe(2)
    module = frame.f_globals.get("__name__", "__main__")
    return module.split(".")[-1] if module else "unknown"


def get_caller_info() -> tuple:
    """
    Get caller file, function, line from the call stack.

    Returns:
        Tuple of (module, function, line)
    """
    # Skip: get_caller_info -> ... -> clog (2 frames minimum)
    frame = sys._getframe(2)
    name = frame.f_globals.get("__name__", "__main__")
    func = frame.f_code.co_name
    line = frame.f_lineno
    module = name.split(".")[-1] if name else "unknown"
    return module, func, line
