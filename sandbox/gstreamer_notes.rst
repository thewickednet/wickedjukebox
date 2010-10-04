Example Chains
==============================================================================

Save an mp3 stream to a file with fixed bitrate::

   gst-launch audiotestsrc ! \
      lamemp3enc bitrate=128 ! \
      filesink location=/tmp/tst.mp3

Stream mp3-data to ALSA::

   FILENAME="/home/exhuma/Desktop/mp3/autotag/Neko Case/Middle Cyclone/01 This Tornado Loves You.mp3" \
   gst-launch filesrc location=$FILENAME ! \
      mad ! \
      alsasink

Convert the same file to ogg-vorbis::

   gst-launch filesrc location=$FILENAME ! \
      mad ! \
      audioconvert ! \
      vorbisenc ! \
      oggmux ! \
      filesink location=/tmp/tst.ogg

Same, but converting to AC-3::

   gst-launch filesrc location=$FILENAME ! \
      mad ! \
      audioconvert ! \
      ffenc_ac3 ! \
      ffmux_ac3 ! \
      filesink location=/tmp/tst.ogg

Passing an MP3 file to shoutcast::

    gst-launch filesrc location=$FILENAME ! \
      shout2send \
         ip=<server-ip> \
         port=<server-port> \
         password=<icecast source-passwd> \
         mount=<mount name>

Ubuntu 10.04 Bug!
==============================================================================

The package gstreamer-plugins-good is broken in Ubuntu 10.04. The gstreamer PPA
includes a more up-to-date package which fixes this problem. To fix this
execute the following commands::

   sudo apt-add-repository ppa:gstreamer-developers/ppa
   sudo aptitude update

This should make the package available. Next::

   sudo aptitude upgrade

See https://bugs.launchpad.net/ubuntu/+source/gst-plugins-good0.10/+bug/569651


Known shout2send parameters
==============================================================================


Connection parameters
------------------------------------------------------------------------------

===========  ==========  ==========
Param Name   Param Type  Access
===========  ==========  ==========
ip           string      Read/Write
port         int         Read/Write
password     string      Read/Write
username     string      Read/Write
streamname   string      Read/Write
description  string      Read/Write
genre        string      Read/Write
protocol     enum        Read/Write
mount        string      Read/Write
url          string      Read/Write
===========  ==========  ==========

