Maintenance
===========

Setting up a development environment
------------------------------------

The project requires a database during development. The connection string to
that DB is located in two locations:

* ``alembic.ini`` (for alembic migrations)
* ``.wicked/wickedjukebox/config.ini`` (for the main application)

For convenience, using fabric_ an environment can be created using::

    fab develop

.. note::
   During the task, an editor will pop up with the config-file template of
   both configs. Review the contents, save & close to continue.

   If the target file already exists and contains differences to the template
   (very likely on subsequent runs), a diff is opened up. **The target file
   will be overwritten with the temporary file!** So recover all necessary
   changes from the target file (the "right" side of the diff) into the
   temporary file (the "left" side of the diff) before saving & closing.

This process will:

* Create a virtual environment with all the necessary dependencies
* Start a background docker-container with a database
* Create ``alembic.ini`` and ``config.ini`` with the appropriate connection
  string for that database.
* Bring the docker-based DB up to the latest schema version


Scanning Music Files
--------------------

To insert music metadata into the database, run::

    ./env/bin/jukebox-admin rescan /path/to/mp3s


Running MPD
-----------

The ``fabfile`` contains a task to run an MPD instance inside a container
(music should become audible on localhost)::

    fab run-mpd -m /path/to/mp3s

.. note::
   If MPD runs inside a docker-container, the path to music files will most
   likely differ from the host. Use path-mapping to make this work. See
   :py:class:`wickedjukebox.component.player.MpdPlayer` for a config example.


Running a test-instance
-----------------------

In order to run the application, a channel must exist in the database. At the
time of this writing, this is not yet automated and must be done by hand.


Accessing the Database
----------------------

When using the development DB inside docker, it can be accessed using the
following command::

    docker exec -ti jukeboxdb mysql -u jukebox -p jukebox

The default password for that instance is ``jukebox``


Modifying the Database Schema
-----------------------------

Database modifications are handled using alembic_ and the environment is set up
to allow auto-generation of migrations. So to apply changes the workflow is as
follows:

* Edit any schema file in the ``wickedjukebox/model/db`` folder
* Run ``./env/bin/alembic revision -m <message> --auto-generate``
* Review the script using ``./env/bin/alembic edit head``
* Apply the changes using ``./env/bin/alembic upgrade head``


.. _fabric: https://fabfile.org
.. _alembic: https://alembic.sqlalchemy.org
