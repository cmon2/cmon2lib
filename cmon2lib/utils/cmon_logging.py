from loguru import logger

# Set up a harmonized logger for cmon2lib using loguru

def clog(level, msg, *args, **kwargs):
    """Central logging gateway for cmon2lib. Usage: clog('info', 'message')"""
    if hasattr(logger, level):
        getattr(logger, level)(msg, *args, **kwargs)
    else:
        logger.info(msg, *args, **kwargs)