.. _configuration:

Configuration
=============

The application configuration is conceptually split into two parts: The "core"
configuration and the "module" configuration.


Core Configuration
------------------

The core configuration contains options which impact the whole wickedjukebox
system independent of channels. At the time of this writing, this only contains
the database connection string (the DSN).


Module Configuration
--------------------

``wickedjukebox`` is composed of different modules, each implementing certain
aspects of the application behaviour. The most important module is the
``player`` module. This is responsible to play music files. Without this module
the jukebox will not play anything.

.. toctree::
   :maxdepth: 2
   :caption: Modules:
   :glob:

   modules/*


Example Configuration
---------------------

.. literalinclude:: ../config.ini.dist
    :language: ini
    :caption: Example Configuration
