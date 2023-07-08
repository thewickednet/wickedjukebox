FROM python:3-slim AS build
ADD . /local/src/wickedjukebox
RUN python3 -m venv /opt/wickedjukebox
RUN /opt/wickedjukebox/bin/pip install uvicorn
RUN /opt/wickedjukebox/bin/pip install -r /local/src/wickedjukebox/requirements.txt
RUN /opt/wickedjukebox/bin/pip install --no-deps /local/src/wickedjukebox

FROM python:3-slim AS prod
ENV DEBIAN_FRONTEND=noninteractive
RUN useradd -ms /bin/bash wickedjukebox
COPY --from=build /opt/wickedjukebox /opt/wickedjukebox
COPY docker-resources/entrypoint.bash /
COPY docker-resources/healthcheck.bash /
RUN apt-get update && apt-get install -y curl
RUN chmod +x /entrypoint.bash
RUN chmod +x /healthcheck.bash
RUN chown -R wickedjukebox /opt/wickedjukebox
USER wickedjukebox
ENTRYPOINT ["/entrypoint.bash"]
EXPOSE 8000

FROM prod AS dev
ENV DEBIAN_FRONTEND=noninteractive
USER root
RUN apt-get update && apt-get install -y \
    sudo \
    git
ADD docker-resources/sudoers-wickedjukebox /etc/sudoers.d/wickedjukebox
RUN usermod -aG sudo wickedjukebox
COPY docker-resources/dev-entrypoint.bash /
RUN chmod +x /dev-entrypoint.bash
USER wickedjukebox
ENTRYPOINT ["/dev-entrypoint.bash"]
