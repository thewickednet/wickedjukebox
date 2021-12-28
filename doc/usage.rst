Usage
=====

After :ref:`installing <installation>` and :ref:`configuration <configuration>`,
the package provides two command-line executables: ``run-channel`` and
``jukebox-admin``.

Both are available in the binary folder of your installation. Depending on your
installation procedure this will be one of the following:

* ``/usr/local/bin`` (when installing system-wide)
* ``~/.local/bin`` (when installing in user-mode)
* ``/path/to/your/virtual-env/bin`` (when installing using a virtual environment)


jukebox-admin
-------------

This tool currently provides only one sub-command: ``rescan``

This is necessary to run after adding new music files to the system. This
recursively walks over the files and inserts/updates their meta-data in the
database.

For more information run:

.. code-block:: bash

    jukebox-admin rescan --help


Example Execution
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    jukebox-admin rescan /path/to/mp3s/to/scan

run-channel
-----------

This tool runs the main process. It requires the channel-name as mandatory
argument. The channel-name maps to the config-file sections to set up the
process.

For more information run:

.. code-block:: bash

    run-channel --help

Example Execution
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    run-channel -c example -v
