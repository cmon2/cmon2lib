__version__ = "0.1.3"

from .utils.cmon_logging_clog import clog, init_clog
from .utils.cmon_logging_cprint import cprint

__all__ = ["clog", "cprint", "init_clog", "__version__"]
