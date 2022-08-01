import logging


def set_up_logging_config(debug_mode_on: bool) -> None:
    if debug_mode_on:
        format = "%(levelname)s:%(asctime)s:%(module)s:%(lineno)d:%(message)s"
        log_level = logging.DEBUG
    else:
        format = "%(message)s"
        log_level = logging.INFO

    logging.basicConfig(level=log_level, format=format)
