import logging
from pathlib import Path

FORMAT = "[%(asctime)s,%(msecs)d] %(name)s [%(levelname)s] %(message)s"
LOG_FILENAME = Path("log.txt")
LOG_LEVEL = logging.DEBUG

logging.basicConfig(
    filename=LOG_FILENAME,
    filemode="w",
    format=FORMAT,
    datefmt="%H:%M:%S",
    level=LOG_LEVEL,
)
log = logging.getLogger("lsp")
