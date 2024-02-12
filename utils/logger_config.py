import logging
import os
import datetime
import inspect


def setup_logger():
    # Get the name of the calling module (script)
    calling_module_name = inspect.stack()[1][0].f_globals['__name__']

    # Create a custom logger
    logger = logging.getLogger(calling_module_name)
    logger.setLevel(logging.DEBUG)

    filename_info = f"info_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}_.log"
    filename_debug = f"debug_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}_.log"

    # Create handlers
    f_handler_debug = logging.FileHandler(os.path.join(os.getcwd(), 'utils', 'logs', filename_debug))
    f_handler_debug.setLevel(logging.DEBUG)

    f_handler = logging.FileHandler(os.path.join(os.getcwd(), 'utils', 'logs', filename_info))
    f_handler.setLevel(logging.INFO)

    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.ERROR)

    # Create formatters and add it to handlers
    f_format_debug = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler_debug.setFormatter(f_format_debug)

    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)

    # Add handlers to the logger
    logger.addHandler(f_handler_debug)
    logger.addHandler(f_handler)
    logger.addHandler(c_handler)

    return logger
