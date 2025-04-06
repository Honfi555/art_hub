from .authorization import authorization_router
from .users import users_router
from .feed import feed_router

__all__: list[str] = ["authorization_router", "feed_router", "users_router"]
__version__: str = "0.2.0"
__author__: str = "honfi555"
__email__: str = "kasanindaniil@gmail.com"
