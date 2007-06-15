#!/bin/bash
if [ $# -ne 1 ]; then exit; fi;
sqlite3 \
   -column \
   -header \
   library.sqlite \
   "SELECT s.localpath
   FROM song_has_genre sg INNER JOIN song s ON (sg.song_id = s.id)\
   WHERE sg.genre_id=$1\
   ORDER BY localpath"
