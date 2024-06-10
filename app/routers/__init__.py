from .note_endpoints import note_router
from .user_endpoints import user_router
from .music_endpoints import music_router
from .recommendation_endpoints import recommendation_router


__all__ = ("note_router", "user_router",
           "music_router", "recommendation_router")
