from importlib.metadata import version
from logging import NullHandler, getLogger

from .debug import DebugTracer, RequestTracer, get_debug_queries
from .ext import FlaskStorm
from .utils import create_context_local, find_flask_storm

logger = getLogger(__name__)
logger.addHandler(NullHandler())

__version__ = version("Flask-Storm")

__all__ = [
    "DebugTracer",
    "FlaskStorm",
    "RequestTracer",
    "create_context_local",
    "find_flask_storm",
    "get_debug_queries",
    "store",
]

#: Shorthand for :attr:`FlaskStorm.store` which does not depend on knowing
#: the FlaskStorm instance bound to the current request context. This is the
#: prefered method of accessing the Store, since using the
#: :attr:`FlaskStorm.store` property directly makes it easy to accidentally
#: create circular imports.
store = create_context_local(None)
