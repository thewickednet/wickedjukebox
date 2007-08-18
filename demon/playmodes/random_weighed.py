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
from demon.util import config

# setup song scoring coefficients
playRatio   = int(getSetting('scoring_ratio',        4))
lastPlayed  = int(getSetting('scoring_lastPlayed',   7))
songAge     = int(getSetting('scoring_songAge',      0))
neverPlayed = int(getSetting('scoring_neverPlayed', 10))

def get():
   """
   determine a song that would be best to play next and add it to the
   prediction queue
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
         log.err( str(ex) )
         log.err( 'Query was: %s' % dpl.query )
      except:
         log.err()

   if config['database.type'] == 'sqlite':
      query = """
         SELECT
            s.id,
            localpath,
            CASE
               WHEN played ISNULL OR skipped ISNULL THEN 0
            ELSE
               CASE
                  WHEN (played+skipped>=10) THEN (( CAST(played as real)/(played+skipped))*%(playRatio)d)
                  ELSE 0.5*%(playRatio)d
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
   elif config['database.type'] == 'mysql':
      query = """
        SELECT s.id, s.localpath,
           IFNULL( IF(played+skipped>=10, (played/(played+skipped))*%(playRatio)d, 0.5*%(playRatio)d), 0)
              + (IFNULL( least(604800, time_to_sec(timediff(NOW(), lastPlayed))), 604800)-604800)/604800*%(lastPlayed)d
              + IF( lastPlayed IS NULL, %(neverPlayed)d, 0)
              * IFNULL( IF( time_to_sec(timediff(NOW(),added))<1209600, time_to_sec(timediff(NOW(),added))/1209600*%(songAge)d, 0), 0) AS score
        FROM song s LEFT JOIN channel_song_data c ON (c.song_id=s.id)
        %(where)s
        ORDER BY score DESC, rand()
        LIMIT 10 OFFSET 0
      """ % {
         'neverPlayed': neverPlayed,
         'playRatio':   playRatio,
         'lastPlayed':  lastPlayed,
         'songAge':     songAge,
         'where':       whereClause,
      }

   resultProxy = dbText(query, engine=dbMeta.engine).execute()
   res = resultProxy.fetchall()
   try:
      out = (res[0][0], res[0][1], float(res[0][2]))
      log.msg("Selected song (%d, %s) via smartget. Score was %4.3f" % out)
      sess = create_session()
      selectedSong = sess.query(Song).selectfirst_by(Song.c.id == out[0] )
      sess.close()
      return selectedSong
   except IndexError:
      log.err('No song returned from query. Is the database empty?')
      return None

