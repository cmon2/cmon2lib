from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
)

def clog(level, msg, *args, **kwargs):
    """Central logging gateway for cmon2lib. Usage: clog('info', 'message')"""
    level_upper = level.upper()
    if hasattr(logger, level_upper):
        logger.opt(depth=2).log(level_upper, msg, *args, **kwargs)
    else:
        logger.opt(depth=2).warning(f"Invalid log level '{level}', defaulting to INFO: {msg}", *args, **kwargs)