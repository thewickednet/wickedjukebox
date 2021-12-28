.. _mpd_inside_docker:

MPD Inside Docker
=================

It *is* possible to run ``mpd`` inside a docker container. You need a container
with Pulse Audio and MPD. Here are example files:

.. literalinclude:: ../../Dockerfile
    :language: Docker
    :caption: Dockerfile

.. literalinclude:: ../../docker-resources/pulse-client.conf
    :language: cfg
    :caption: pulse-client.conf

.. literalinclude:: ../../docker-resources/mpd.conf
    :language: cfg
    :caption: mpd.conf

Assuming the docker-image has been run with the tag ``wickedjukebox/mpd``, the
container can then be run using:

.. code-block:: bash

    docker run --rm \
        --volume=/run/user/${UID}/pulse:/run/user/${UID}/pulse \
        --volume=/path/to/local/mp3s:/var/lib/mpd/music:ro \
        --name wickedjukebox_mpd  \
        -p 6600:6600  \
        wickedjukebox/mpd
