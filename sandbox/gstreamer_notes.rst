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

