"""Rich console output for UI messages (cprint)."""

from loguru import logger


def cprint(level: str, msg: str, *args):
    """
    Rich console output for UI messages (tree views, formatted tables, etc.).

    Does NOT log to file - pure console output with Rich markup support.
    Uses loguru directly with colorize=True for Rich markup.

    Usage:
        cprint('info', '[green]✓[/green] Item synced')
        cprint('info', '[cyan]Source:[/cyan] {}', source_name)
        cprint('warning', '[yellow]![/yellow] Something may be wrong')

    Args:
        level: Log level (trace, debug, info, success, warning, error, critical)
        msg: Log message (supports {} formatting, Rich markup)
        *args: Format arguments for msg
    """
    if args:
        msg = msg.format(*args)

    level_upper = level.upper()

    valid_levels = {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}
    if level_upper not in valid_levels:
        level_upper = "INFO"

    # Log to stderr with Rich markup support
    logger.opt(depth=2).log(level_upper, msg)
