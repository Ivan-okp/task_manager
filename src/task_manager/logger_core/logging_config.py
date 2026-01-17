"""
Конфигурация логирования проекта. Этот модуль настраивает систему логирования.
"""

import logging
from pathlib import Path

from colorlog import ColoredFormatter

current_file = Path(__file__).resolve()
src_dir = current_file.parent.parent
log_dir = src_dir / "logs"

log_dir.mkdir(
    parents=True,
    exist_ok=True
)

log_file_path = log_dir / "app.log"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_formatter = ColoredFormatter(
    fmt="%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
)
file_formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename=str(log_file_path), encoding="utf-8")

console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
