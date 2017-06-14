from logging import getLogger, NullHandler

from .debug import DebugTracer, get_debug_queries, RequestTracer
from .ext import FlaskStorm
from .utils import find_flask_storm, create_context_local

logger = getLogger(__name__)
logger.addHandler(NullHandler())

__version__ = "0.1.2"

__all__ = [
    "create_context_local",
    "DebugTracer",
    "FlaskStorm",
    "find_flask_storm",
    "get_debug_queries",
    "RequestTracer",
    "store",
]

#: Shorthand for :attr:`FlaskStorm.store` which does not depend on knowing
#: the FlaskStorm instance bound to the current request context. This is the
#: prefered method of accessing the Store, since using the
#: :attr:`FlaskStorm.store` property directly makes it easy to accidentally
#: create circular imports.
store = create_context_local(None)
