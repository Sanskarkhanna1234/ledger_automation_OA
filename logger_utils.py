import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Callable
import functools

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

STEP_LOG_PATH = os.path.join(LOG_DIR, "steps.log")
RESULT_LOG_PATH = os.path.join(LOG_DIR, "result.log")
DEBUG_LOG_PATH = os.path.join(LOG_DIR, "debug.log")

def _build_file_handler(path: str, level: int) -> RotatingFileHandler:
    handler = RotatingFileHandler(path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    return handler

def setup_loggers():
    # file-only loggers; do not propagate to root console
    steps = logging.getLogger("steps")
    if not steps.handlers:
        steps.setLevel(logging.INFO)
        steps.addHandler(_build_file_handler(STEP_LOG_PATH, logging.INFO))
        steps.propagate = False

    result = logging.getLogger("result")
    if not result.handlers:
        result.setLevel(logging.INFO)
        result.addHandler(_build_file_handler(RESULT_LOG_PATH, logging.INFO))
        result.propagate = False

    debugfile = logging.getLogger("debugfile")
    if not debugfile.handlers:
        debugfile.setLevel(logging.DEBUG)
        debugfile.addHandler(_build_file_handler(DEBUG_LOG_PATH, logging.DEBUG))
        debugfile.propagate = False

def get_step_logger() -> logging.Logger:
    setup_loggers()
    return logging.getLogger("steps")

def get_result_logger() -> logging.Logger:
    setup_loggers()
    return logging.getLogger("result")

def get_debug_file_logger() -> logging.Logger:
    setup_loggers()
    return logging.getLogger("debugfile")

# logger_utils.py
def log_step(name: str) -> Callable:
    """Decorator to auto-log with clean console tags."""
    steps = get_step_logger()
    result = get_result_logger()
    debugf = get_debug_file_logger()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # console sees this line (because it has [DEBUG])
            steps.info("[DEBUG] %s — START", name)
            # file-only deep trace
            debugf.debug("START %s args=%s kwargs=%s", name, args, kwargs)
            try:
                out = func(*args, **kwargs)
                # console sees only this PASS line
                result.info("[SUCCESS] %s", name)
                steps.info("[DEBUG] %s — END (PASS)", name)
                return out
            except Exception as e:
                # console sees only this FAIL line
                result.error("[FAIL] %s — %s", name, e)
                steps.error("[DEBUG] %s — END (FAIL) — %s", name, e)
                raise
        return wrapper
    return decorator
step_log: logging.Logger = get_step_logger()
result_log: logging.Logger = get_result_logger()
debug_log: logging.Logger = get_debug_file_logger()

