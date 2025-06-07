from loguru import logger

# Set up a harmonized logger for cmon2lib using loguru

def clog(level, msg, *args, **kwargs):
    """Central logging gateway for cmon2lib. Usage: clog('info', 'message')"""
    # Use loguru's depth=2 so the log record points to the caller of clog, not clog itself
    if hasattr(logger, level):
        logger.opt(depth=2).log(level.upper(), msg, *args, **kwargs)
    else:
        logger.opt(depth=2).info(msg, *args, **kwargs)