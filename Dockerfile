FROM python:3-slim AS build
ADD . /local/src/wickedjukebox
RUN python3 -m venv /opt/wickedjukebox
RUN /opt/wickedjukebox/bin/pip install uvicorn
RUN /opt/wickedjukebox/bin/pip install -r /local/src/wickedjukebox/requirements.txt
RUN /opt/wickedjukebox/bin/pip install --no-deps /local/src/wickedjukebox

FROM python:3-slim
COPY --from=build /opt/wickedjukebox /opt/wickedjukebox
COPY docker-resources/entrypoint.bash /
RUN chmod +x /entrypoint.bash
ENTRYPOINT ["/entrypoint.bash"]
EXPOSE 8000
