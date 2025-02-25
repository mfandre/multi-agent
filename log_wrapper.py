import os
import logging
from logging.handlers import RotatingFileHandler

FILE = False
LEVEL = logging.DEBUG

log_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s"
)

# Setting log config
my_handler = None
if FILE:
    LOGFILE = "log.txt"
    my_handler = RotatingFileHandler(
        LOGFILE,
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=2,
        encoding=None,
        delay=0,
    )
else:
    my_handler = logging.StreamHandler()
my_handler.setFormatter(log_formatter)
my_handler.setLevel(LEVEL)

app_log = logging.getLogger("root")
app_log.setLevel(LEVEL)

app_log.addHandler(my_handler)