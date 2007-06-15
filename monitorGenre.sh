#!/bin/bash
sqlite3 \
   -column \
   -header \
   library.sqlite \
   "SELECT g.id, g.name, COUNT(*)\
   FROM song_has_genre sg LEFT OUTER JOIN genre g ON (sg.genre_id = g.id)\
   GROUP BY g.name\
   ORDER BY COUNT(*)"
