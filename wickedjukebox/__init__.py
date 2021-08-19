# pylint: disable=missing-docstring

import importlib.metadata


__version__ = importlib.metadata.version("wickedjukebox")


#: The name of the environment variable controlling the config location
ENV_CONF = 'WICKEDJB_CONFIG_FOLDER'
