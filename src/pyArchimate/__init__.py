import os
import sys
from collections import defaultdict

import lxml.etree as et

from .helpers.diagram import get_or_create_connection, get_or_create_node
from .helpers.logging import log, log_set_level, log_to_file, log_to_stderr
from .helpers.properties import check_invalid_conn, check_invalid_nodes, embed_props, expand_props
from .pyArchimate import *  # noqa: F401,F403
