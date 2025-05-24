import logging

# Set up a harmonized logger for cmon2lib
logger = logging.getLogger("cmon2lib")
logger.setLevel(logging.INFO)  # Default level, can be changed by user
handler = logging.StreamHandler()
formatter = logging.Formatter('[cmon2lib] %(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

def clog(level, msg, *args, **kwargs):
    """Central logging gateway for cmon2lib. Usage: clog('info', 'message')"""
    if hasattr(logger, level):
        getattr(logger, level)(msg, *args, **kwargs)
    else:
        logger.info(msg, *args, **kwargs)
