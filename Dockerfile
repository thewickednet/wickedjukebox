FROM ubuntu:16.04
MAINTAINER Michel Albert <michel@albert.lu>

ENV UNAME mpduser

# Install everything needed for MPD via Pulse (and a client for convenience)
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
    pulseaudio-utils \
    mpd \
    ncmpcpp

# Add a separate user to be able to run the process in user-space and set up
# required folders
RUN adduser --disabled-password --uid 1000 ${UNAME} && \
    usermod -a -G audio ${UNAME} && \
    install -o ${UNAME} -d /var/lib/mpd && \
    install -o ${UNAME} -d /run/mpd

# Inject the config files needed for pulse and mpd
COPY docker-resources/pulse-client.conf /etc/pulse/client.conf
COPY docker-resources/mpd.conf /etc/mpd.conf
RUN chown ${UNAME} /etc/mpd.conf && \
    chown -R ${UNAME} /var/log/mpd

USER $UNAME
ENV HOME /home/${UNAME}

ENTRYPOINT ["mpd", "-v", "--stdout", "--no-daemon"]
