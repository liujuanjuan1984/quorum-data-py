import logging

from quorum_data_py import converter, feed
from quorum_data_py.trx_type import get_trx_type

__version__ = "1.1.1"
__author__ = "liujuanjuan1984"

# Set default logging handler to avoid "No handler found" warnings.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

logger.info("quorum_data_py version: %s", __version__)
