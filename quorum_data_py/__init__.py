import logging

from quorum_data_py import converter, feed, util
from quorum_data_py.trx_type import get_trx_type

__version__ = "1.3.1"
__author__ = "liujuanjuan1984"

# Set default logging handler to avoid "No handler found" warnings.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

logger.info("Version %s", __version__)
