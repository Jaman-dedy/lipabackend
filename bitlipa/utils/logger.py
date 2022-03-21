import logging
import coloredlogs

from .get_object_attr import get_object_attr


def logger(data=None, type=None):
    logger = logging.getLogger(__name__)
    coloredlogs.install(logger=logger)
    get_object_attr(logger, type, logger.info)(f'LOGGER: >>> {data}')
