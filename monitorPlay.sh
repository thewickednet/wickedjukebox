#!/bin/bash
sqlite3 \
   -column \
   -header \
   library.sqlite \
   "SELECT s.id, md.played, md.skipped, a.name, s.title, md.lastPlayed \
   FROM channel_song_data md INNER JOIN song s ON ( md.song_id = s.id )\
   INNER JOIN artist a ON (s.artist_id = a.id) \
   ORDER BY lastPlayed DESC LIMIT 0,10"
