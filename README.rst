INSTALLATION
============

System dependencies
-------------------

::

   sudo aptitude install python3 python3-pip python-gst0.10 \
                         python3-dev libmysqlclient-dev build-essential \
                         libshout-dev icecast2

Virtual Environment & Installation
----------------------------------

::

   pyvenv /opt/wickedjukebox
   /opt/wickedjukebox/bin/pip install .


USAGE
=====

The shell scripts are installed into you virtual environment. You can either
"activate" the environment, or run the script directly from
``/opt/wickedjukebox/bin/script-name``

Running the scripts without activating the environment is recommended.

Available scripts:

   ``jukebox-admin.py``
      Script to manage your collection

   ``run_channel.py``
      Script to start a specific channel


Development
===========

For development tasks, this project uses fabric_ and pipenv_. The easiest way
to install everything is to install ``pipenv`` as user an use ``fabric`` from
there::

   pip install --user pipenv
   export PATH=~/.local/bin:$PATH
   pipenv install -de .


Once installed, you can set up a running development environment by running::

   fab develop

You can open a sub-shell using ``pipenv shell`` in which the executables from
the jukebox will be available.


.. _fabric: http://www.fabfile.org
.. _pipenv: https://docs.pipenv.org
