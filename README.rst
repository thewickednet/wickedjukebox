INSTALLATION
============

System dependencies
-------------------

::

   sudo aptitude install python-setuptools python-virtualenv python-gst0.10 \
                         python-dev libmysqlclient-dev build-essential \
                         libshout-dev icecast2

Virtual Environment
-------------------

::

   virtualenv /path/to/environment

Install the package
-------------------

   /path/to/environment/bin/python setup.py install

USAGE
=====

The shell scripts are installed into you virtual environment. You can either
"activate" the environment, or run the script directly from
/path/to/environment/bin/script-name.

Running the scripts without activating the environment is recommended.

Available scripts:

   jukebox-admin.py
      Script to manage your collection

   run_channel.py
      Script to start a specific channel


Development
===========

For development tasks, this project uses fabric_. Once installed, you can set
up a running development environment by running::

    fab develop

This will set up a virtual environment ``env`` in the current folder and link
the source files into this environment.


.. _fabric: http://www.fabfile.org
