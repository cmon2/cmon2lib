"""Format functions for logging output."""


def format_log_record(record: dict) -> str:
    """
    Format for file logging: full metadata with timestamp, level, module, user.

    Args:
        record: Loguru record dict with time, level, name, function, line, extra, message.

    Returns:
        Formatted log line: YYYY-MM-DD HH:mm:ss | LEVEL | module:func:line | USER | message
    """
    timestamp = record["time"].strftime("%Y-%m-%d %H:%M:%S")
    level = record["level"].name.ljust(8)
    name = record["name"]
    function = record["function"]
    line = record["line"]
    user = record["extra"].get("user", "unknown")
    message = record["message"]
    return f"{timestamp} | {level} | {name}:{function}:{line} | {user} | {message}"


def format_console(record: dict) -> str:
    """
    Format for console output: message only with color.

    WARNING/ERROR get a level prefix.

    Args:
        record: Loguru record dict with level, message.

    Returns:
        Formatted console message with optional color/prefix.
    """
    level = record["level"].name
    message = record["message"]

    if level == "WARNING":
        return f"<yellow>WARNING:</yellow> {message}"
    elif level == "ERROR":
        return f"<red>ERROR:</red> {message}"
    elif level == "CRITICAL":
        return f"<red>CRITICAL:</red> {message}"
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
