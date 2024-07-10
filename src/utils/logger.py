import csv
import io
import logging

logging.basicConfig(format="%(message)s", level=logging.DEBUG)


def create_logger(name):
    return logging.getLogger(name)


def init_default_logger(log_level):
    default_logger = create_logger("default")
    default_logger.propagate = True

    return default_logger
