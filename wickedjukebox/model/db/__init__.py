"""
This sub-package contains the database model for the application.
"""

# These imports must exist for the alembic auto-generation to properly pick up
# the schema. The imports must happen *somewhere*. I decided to do this here for
# simplicity, but it annoys me that they are only here for alembic. There may be
# a better way but at the time of this writing I had no motivation to look for
# one :)

from . import (
    auth,
    events,
    lastfm,
    library,
    logging,
    playback,
    settings,
    stats,
    webui,
)

__all__ = [
    "auth",
    "events",
    "lastfm",
    "library",
    "logging",
    "playback",
    "settings",
    "stats",
    "webui",
]
