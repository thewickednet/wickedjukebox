#!/bin/bash

# ----------------------------------------------------------------------------
# This script generates a collection of MP3 files containing nothing but a
# plain sine-wave of length 1min.
#
# The files contain basic metadata and can be used for testing purposes
# ----------------------------------------------------------------------------

set -e

ROOT=sampledata

function createAlbum {
    artist="${1}"
    name="${2}"
    folder="${ROOT}/${artist}/${album}"
    mkdir -p "${folder}"
    for i in {1..5}; do
        title="song-${i}"
        filename="${folder}/${title}.mp3"
        ffmpeg \
            -f lavfi \
            -loglevel error \
            -y \
            -i "sine=frequency=500:duration=60" \
            -metadata artist=${artist} \
            -metadata album=${album} \
            -metadata title=${title} \
            -metadata track=${i} \
            "${filename}"
        echo "Successfully generated ${filename}"
    done
}

for j in {1..3}; do
    artist="artist-${j}"
    for i in {1..3}; do
        album="album-${i}"
        createAlbum "${artist}" "${album}"
    done
done
