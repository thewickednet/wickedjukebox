FROM python:3-slim
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    libmysqlclient-dev \
    wget \
    vim

COPY docker/dist/config.ini /etc/wicked/wickedjukebox/
COPY dist/*.whl /tmp
RUN python3 -m venv /opt/jukebox
RUN /opt/jukebox/bin/pip install /tmp/*.whl
