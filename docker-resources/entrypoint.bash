#!/bin/bash

exec /opt/wickedjukebox/bin/uvicorn \
    --host "0.0.0.0" \
    --port "8000" \
    wickedjukebox.asgi:application
