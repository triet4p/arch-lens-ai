import logging
import os
import sys
from datetime import datetime
from typing import Dict
from src.app.core.config import settings

_LOGGER_CACHE: Dict[str, logging.Logger] = {}

LEVEL_MAPPING = {
    "INFO": logging.INFO, "ERROR": logging.ERROR,
    "WARNING": logging.WARNING, "DEBUG": logging.DEBUG, "FATAL": logging.FATAL,
}

_LOGGING_LEVEL = LEVEL_MAPPING[settings.LOGGING_LEVEL]
_LOGGING_HANDLER = settings.LOGGING_HANDLER.lower()
_LOGGING_FILE_DIR = settings.LOGGING_FILE_DIR

def get_logger(log_id: str) -> logging.Logger:
    global _LOGGER_CACHE
    if log_id in _LOGGER_CACHE:
        return _LOGGER_CACHE[log_id]
    
    _logger = logging.getLogger(log_id)
    _logger.setLevel(_LOGGING_LEVEL)
    
    if _logger.hasHandlers():
        _logger.handlers.clear()
        
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s by %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    if _LOGGING_HANDLER in ["console", "both"]:
        _handler = logging.StreamHandler(sys.stdout)
        _handler.setFormatter(formatter)
        _logger.addHandler(_handler)

    if _LOGGING_HANDLER in ["file", "both"] and _LOGGING_FILE_DIR:
        try:
            expanded_dir = os.path.expanduser(_LOGGING_FILE_DIR) if _LOGGING_FILE_DIR.startswith('~') else _LOGGING_FILE_DIR
            abs_dir = os.path.abspath(expanded_dir)
            os.makedirs(abs_dir, exist_ok=True)
            
            now = datetime.now().strftime("%Y%m%d")
            file_path = os.path.join(abs_dir, f"arch_lens_{now}.log")
            
            _file_handler = logging.FileHandler(file_path, encoding='utf-8')
            _file_handler.setFormatter(formatter)
            _logger.addHandler(_file_handler)
        except Exception as e:
            print(f"!! FAILED TO SETUP LOG FILE: {e}", file=sys.stderr)
        
    _LOGGER_CACHE[log_id] = _logger
    return _logger