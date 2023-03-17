import logging

import quorum_data_py.feed as FeedData

__version__ = "1.0.3"
__author__ = "liujuanjuan1984"

# Set default logging handler to avoid "No handler found" warnings.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
