from .note_endpoints import note_router
from .user_endpoints import user_router
from .music_endpoints import music_router
from .reccomendation_endpoints import reccomendation_router


__all__ = ("note_router", "user_router",
           "music_router", "reccomendation_router")
