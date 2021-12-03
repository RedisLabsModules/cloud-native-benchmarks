#  Apache License Version 2.0
#
#  Copyright (c) 2021., Redis Performance Group
#  All rights reserved.
#

import logging
import os

LOG_LEVEL = logging.DEBUG
if os.getenv("VERBOSE", "0") == "0":
    LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s %(levelname)-4s %(message)s"
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"


def log_setup(logname):
    if logname is not None:
        print("Writing log to {}".format(logname))
        logging.basicConfig(
            filename=logname,
            filemode="a",
            format=LOG_FORMAT,
            datefmt=LOG_DATEFMT,
            level=LOG_LEVEL,
        )
    else:
        logger = logging.getLogger()
        logger.setLevel(LOG_LEVEL)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(LOG_LEVEL)

        # create formatter
        formatter = logging.Formatter(LOG_FORMAT)

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)
    print_stdout_effective_log_level()


def print_stdout_effective_log_level():
    effective_log_level = logging.getLogger().getEffectiveLevel()
    if effective_log_level == logging.DEBUG:
        effective_log_level = "DEBUG"
    if effective_log_level == logging.INFO:
        effective_log_level = "INFO"
    if effective_log_level == logging.WARN:
        effective_log_level = "WARN"
    if effective_log_level == logging.ERROR:
        effective_log_level = "ERROR"
    print("Effective log level set to {}".format(effective_log_level))
