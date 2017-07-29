FROM debian:stretch
RUN apt-get update && echo "2017-07-18 11:02:18"
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y icecast2 python-virtualenv gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly python-gst-1.0
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y less
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-setuptools python-dev libmariadbclient-dev build-essential libshout-dev icecast2 python-pip
RUN virtualenv --system-site-packages /opt/jukebox
RUN /opt/jukebox/bin/pip install -U pip
RUN ["sed", "-i", "s/ENABLE=false/ENABLE=true/", "/etc/default/icecast2"]

# --- The following lines (COPY) will break cached docker images!
COPY docker/dist/icecast.xml /etc/icecast2/icecast.xml
COPY docker/dist/config.ini /etc/wicked/wickedjukebox/
COPY . /data
RUN /opt/jukebox/bin/pip install -r /data/requirements.txt
RUN /opt/jukebox/bin/pip install /data
RUN rm -rf /data
