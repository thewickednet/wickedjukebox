#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Weighed random. Different factors are considered when selecting a song at
random. Like the time it was last played, how often it was skipped, and so on.
"""

from demon.plparser import parseQuery, ParserSyntaxError
from demon.model import create_session, DynamicPlaylist, dynamicPLTable, getSetting, metadata as dbMeta, Song
from sqlalchemy import text as dbText
from twisted.python import log
import threading

# setup song scoring coefficients
playRatio   = int(getSetting('scoring_ratio',        4))
lastPlayed  = int(getSetting('scoring_lastPlayed',   7))
songAge     = int(getSetting('scoring_songAge',      0))
neverPlayed = int(getSetting('scoring_neverPlayed', 10))

def findSong():
   """
   determine a song that would be best to play next and return it
   """

   # Retrieve dynamic playlists
   whereClause = ''

   sess = create_session()
   res = sess.query(DynamicPlaylist).select(dynamicPLTable.c.group_id > 0, order_by=['group_id'])
   sess.close()
   for dpl in res:
      try:
         if parseQuery( dpl.query ) is not None:
            whereClause = "AND (%s)" % parseQuery( dpl.query )
         break; # only one query will be parsed. for now.... this is a big TODO
                # as it triggers an unexpected behaviour (bug). i.e.: Why the
                # heck does it only activate one playlist?!?
      except ParserSyntaxError, ex:
         import traceback; traceback.print_exc()
         log.err( str(ex) )
         log.err( 'Query was: %s' % dpl.query )

   ## -- MySQL Query WAS:
   ##   SELECT
   ##      song_id,
   ##      localpath,
   ##      IFNULL( IF(played+skipped>=10, (played/(played+skipped))*%(playRatio)d, 0.5), 0)
   ##         + (IFNULL( least(604800, time_to_sec(timediff(NOW(), lastPlayed))), 604800)-604800)/604800*%(lastPlayed)d
   ##         + IF( played+skipped=0, %(neverPlayed)d, 0)
   ##         + IFNULL( IF( time_to_sec(timediff(NOW(),added))<1209600, time_to_sec(timediff(NOW(),added))/1209600*%(songAge)d, 0), 0) score
   ##   FROM songs
   ##   ORDER BY score DESC, rand()
   ##   LIMIT 0,10
   query = """
      SELECT
         s.id,
         localpath,
         CASE
            WHEN played ISNULL OR skipped ISNULL THEN 0
         ELSE
            CASE
               WHEN (played+skipped>=10) THEN (( CAST(played as real)/(played+skipped))*%(playRatio)d)
               ELSE 0.5
            END
         END +
            CASE WHEN played ISNULL AND skipped ISNULL THEN %(neverPlayed)d
            ELSE 0
            END +
         (CASE WHEN lastPlayed ISNULL THEN 604800 ELSE
             julianday('now')*86400 - julianday(lastPlayed)*86400 -- seconds since last play
         END - 604800)/604800*%(lastPlayed)d +
         CASE WHEN s.added ISNULL THEN 0 ELSE
            CASE WHEN julianday('now')*86400 - julianday(s.added)*86400 < 1209600 THEN
               (julianday('now')*86400 - julianday(s.added)*86400)/1209600*%(songAge)d
            ELSE
               0
            END
         END
            AS score
      FROM song s LEFT JOIN channel_song_data rel ON ( rel.song_id == s.id )
      INNER JOIN artist a ON ( a.id == s.artist_id )
      INNER JOIN album b ON ( b.id == s.album_id )
      %(where)s
      ORDER BY score DESC, RANDOM()
      LIMIT 10 OFFSET 0
   """ % {
      'neverPlayed': neverPlayed,
      'playRatio':   playRatio,
      'lastPlayed':  lastPlayed,
      'songAge':     songAge,
      'where':       whereClause,
   }

   # I won't use ORDER BY RAND() as it is way too dependent on the dbms!
   import random
   random.seed()
   resultProxy = dbText(query, engine=dbMeta.engine).execute()
   res = resultProxy.fetchall()
   randindex = random.randint(1, len(res)) -1
   try:
      out = (res[randindex][0], res[randindex][1], float(res[randindex][2]))
      log.msg("Selected song (%d, %s) via smartget. Score was %4.3f" % out)
      sess = create_session()
      selectedSong = sess.query(Song).selectfirst_by(Song.c.id == out[0] )
      sess.close()
      return selectedSong
   except IndexError:
      import traceback; traceback.print_exc()
      log.err('No song returned from query. Is the database empty?')
      return None

# as the query can take fscking long, we prefetch one song
log.msg( 'prefetching...' )
prefetch = [findSong()]

class Prefetcher( threading.Thread ):
   def run(self):
      global prefetch
      prefetch.append(findSong())

def get():
   pref = Prefetcher()
   pref.start()

   # wait until a song is prefetched (in case two 'gets' are called quickly
   # after another)
   while len(prefetch) == 0:
      pass

   log.msg( "Random song: %s" % prefetch )
   return prefetch.pop()
