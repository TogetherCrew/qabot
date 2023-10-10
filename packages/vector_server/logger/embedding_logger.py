import logging

logging.basicConfig(level=logging.INFO)


def get_logger(name="hivemind"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger


logger = get_logger()
