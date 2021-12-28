.. _installation:

Installation
============

Requirements
------------

.. note::

    ``wickedjukebox`` has so far only been tested on Linux

``wickedjukebox`` requires MPD_ as backend to play music. On startup,
``wickedjukebox`` will open a TCP connection to ``mpd`` and start controlling
its playlist.

For ``mpd``, you can either install the package from your Linux distribution or
run it inside :ref:`docker <mpd_inside_docker>`.


Package Installation
--------------------

``wickedjukebox`` follows the default Python build-process and can be installed
using pip_.

.. tip::

    Consider installing the package inside a `virtual environment`_.

.. code-block:: bash

    pip install <path-to-whl-file>

Or, if no WHL file is available, install directly from ``git``:

.. code-block:: bash

    pip install git+https://path/to/repository.git

.. _pip: https://pypi.org/project/pip/
.. _virtual environment: https://docs.python.org/3/tutorial/venv.html
.. _MPD: https://www.musicpd.org/
