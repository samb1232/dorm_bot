import logging
import sys

class COLOR_CODES:
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    RED_BRIGHT = '\033[31;1m'
    BLACK = '\033[0m'
    DIM = '\033[2m'


def get_logger(name: str) -> logging.Logger:
    COLORS = {
        'DEBUG': COLOR_CODES.CYAN,
        'INFO': COLOR_CODES.GREEN,
        'WARNING': COLOR_CODES.YELLOW,
        'ERROR': COLOR_CODES.RED,
        'CRITICAL': COLOR_CODES.RED_BRIGHT,
    }
    RESET = COLOR_CODES.BLACK
    DIM = COLOR_CODES.DIM
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    if logger.handlers:
        return logger
    
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    
    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            color = COLORS.get(record.levelname, '')
            levelname = f"{color}{record.levelname}{RESET}"
            record.levelname = levelname
            record.asctime = f"{DIM}{self.formatTime(record)}{RESET}"
            return super().format(record)
    
    formatter = ColoredFormatter(
        fmt='{asctime} | {name} | {levelname} | {message}',
        datefmt='%d.%m.%Y %H:%M:%S',
        style='{'
    )
    ch.setFormatter(formatter)
    
    logger.addHandler(ch)
    return logger