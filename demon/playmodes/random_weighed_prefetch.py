#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Weighed random. Different factors are considered when selecting a song at
random. Like the time it was last played, how often it was skipped, and so on.
"""

from demon.plparser import parseQuery, ParserSyntaxError
from demon.model import create_session, DynamicPlaylist, dynamicPLTable, getSetting, metadata as dbMeta, Song, usersTable
from sqlalchemy import text as dbText, func, select
from twisted.python import log
from demon.util import config
from random import random
import threading

prefetch = []

def findSong(channel_id):
   """
   determine a song that would be best to play next and return it
   """
   global prefetch

   # setup song scoring coefficients
   userRating  = int(getSetting('scoring_userRating',   4, channel=channel_id))
   lastPlayed  = int(getSetting('scoring_lastPlayed',   10,channel=channel_id))
   songAge     = int(getSetting('scoring_songAge',      1, channel=channel_id))
   neverPlayed = int(getSetting('scoring_neverPlayed',  4, channel=channel_id))
   randomness  = int(getSetting('scoring_randomness',   1, channel=channel_id))
   max_random_duration = int(getSetting('max_random_duration', 600,  channel=channel_id))
   proofoflife_timeout = int(getSetting('proofoflife_timeout', 120))


   whereClauses = [ "NOT broken" ]
   if prefetch:
      log.msg( "Ignoring song %r from random selection as it was already prefetched!" % prefetch[0] )
      whereClauses.append( "song.id != %d" % prefetch[0].id )

   # Retrieve dynamic playlists
   sess = create_session()
   res = sess.query(DynamicPlaylist).select(dynamicPLTable.c.group_id > 0, order_by=['group_id'])
   sess.close()
   for dpl in res:
      try:
         if parseQuery( dpl.query ) is not None:
            whereClauses.append("(" + parseQuery( dpl.query ) + ")")
         break; # only one query will be parsed. for now.... this is a big TODO
                # as it triggers an unexpected behaviour (bug). i.e.: Why the
                # heck does it only activate one playlist?!?
      except ParserSyntaxError, ex:
         import traceback; traceback.print_exc()
         log.err( str(ex) )
         log.err( 'Query was: %s' % dpl.query )
      except:
         import traceback; traceback.print_exc()
         log.err()

   if config['database.type'] == 'mysql':

      s = select([usersTable], func.unix_timestamp(usersTable.c.proof_of_listening) + proofoflife_timeout > func.unix_timestamp(func.now()))
      r = s.execute()
      if len(r.fetchall()) == 0:
         # no users online
         query = """
            SELECT s.id, s.localpath,
               ((IFNULL( least(604800, time_to_sec(timediff(NOW(), lastPlayed))), 604800)-604800)/604800*%(lastPlayed)d)
                  + IF( lastPlayed IS NULL, %(neverPlayed)d, 0)
                  + IFNULL( IF( time_to_sec(timediff(NOW(),s.added))<1209600, time_to_sec(timediff(NOW(),s.added))/1209600*%(songAge)d, 0), 0)
                  + ((RAND()*%(randomness)f*2)-%(randomness)f)
               AS score
            FROM song s
               LEFT JOIN channel_song_data c ON (c.song_id=s.id)
               INNER JOIN artist a ON ( a.id = s.artist_id )
               INNER JOIN album b ON ( b.id = s.album_id )
            WHERE (%(where)s) AND NOT s.broken AND s.duration < %(max_random_duration)d
            ORDER BY score DESC
            LIMIT 10 OFFSET 0
         """ % {
            'neverPlayed': neverPlayed,
            'userRating':  userRating,
            'lastPlayed':  lastPlayed,
            'songAge':     songAge,
            'randomness':  randomness,
            'max_random_duration': max_random_duration,
            'where':       ") AND (".join(whereClauses).replace("%", "%%"),
         }
      else:
         query = """
            SELECT s.id, s.localpath,
               ((IFNULL( least(604800, time_to_sec(timediff(NOW(), lastPlayed))), 604800)-604800)/604800*%(lastPlayed)d)
                  + ((IFNULL(ls.loves,0)) / (SELECT COUNT(*) FROM users WHERE UNIX_TIMESTAMP(proof_of_listening)+%(proofoflife)d > UNIX_TIMESTAMP(NOW())) * %(userRating)d)
                  + IF( lastPlayed IS NULL, %(neverPlayed)d, 0)
                  + IFNULL( IF( time_to_sec(timediff(NOW(),s.added))<1209600, time_to_sec(timediff(NOW(),s.added))/1209600*%(songAge)d, 0), 0)
                  + ((RAND()*%(randomness)f*2)-%(randomness)f)
               AS score
            FROM song s
               LEFT JOIN channel_song_data c ON (c.song_id=s.id)
               LEFT JOIN (
                  SELECT song_id, COUNT(*) AS loves
                  FROM user_song_standing
                  INNER JOIN users ON(users.id=user_song_standing.user_id)
                  LEFT OUTER JOIN setting ON(users.id=setting.user_id AND setting.var="loves_affect_random")
                  WHERE standing='love' AND IFNULL(setting.value, 1) = 1
                     AND UNIX_TIMESTAMP(proof_of_listening)+%(proofoflife)d > UNIX_TIMESTAMP(NOW())
                  GROUP BY song_id
               ) ls ON (s.id=ls.song_id)
               LEFT JOIN (
                  SELECT song_id, COUNT(*) AS hates
                  FROM user_song_standing
                  INNER JOIN users ON(users.id=user_song_standing.user_id)
                  LEFT OUTER JOIN setting ON(users.id=setting.user_id AND setting.var="hates_affect_random")
                  WHERE standing='hate' AND IFNULL(setting.value, 1) = 1
                     AND UNIX_TIMESTAMP(proof_of_listening)+%(proofoflife)d > UNIX_TIMESTAMP(NOW())
                  GROUP BY song_id
               ) hs ON (s.id=hs.song_id)
               INNER JOIN artist a ON ( a.id = s.artist_id )
               INNER JOIN album b ON ( b.id = s.album_id )
            WHERE (%(where)s) AND IFNULL(hs.hates,0) = 0 AND NOT s.broken AND s.duration < %(max_random_duration)d
            ORDER BY score DESC
            LIMIT 10 OFFSET 0
         """ % {
            'neverPlayed': neverPlayed,
            'userRating':  userRating,
            'lastPlayed':  lastPlayed,
            'proofoflife': proofoflife_timeout,
            'randomness':  randomness,
            'songAge':     songAge,
            'max_random_duration': max_random_duration,
            'where':       ") AND (".join(whereClauses).replace("%", "%%"),
         }
   else:
      raise Error("SQLite support discontinued since revision 346. It may reappear in the future!")

   resultProxy = dbText(query, engine=dbMeta.engine).execute()
   res = resultProxy.fetchall()
   try:
      if res[0][2] is None:
         # no users are online!
         return None
      out = (res[0][0], res[0][1], float(res[0][2]))
      log.msg("Selected song (%d, %s) via smartget. Score was %4.3f" % out)
      sess = create_session()
      selectedSong = sess.query(Song).selectfirst_by(Song.c.id == out[0] )
      sess.close()
      return selectedSong
   except IndexError:
      import traceback; traceback.print_exc()
      log.err('No song returned from query. Is the database empty?')
      return None

class Prefetcher( threading.Thread ):

   _channel_id = None

   def __init__(self, channel_id):
      threading.Thread.__init__(self)
      self._channel_id = channel_id

   def run(self):
      global prefetch
      log.msg( "Background prefetching... " )
      song = findSong(self._channel_id)
      log.msg( "  ... prefetched %r" % song )
      prefetch.append(song)

def get(channel_id):
   pref = Prefetcher(channel_id)
   pref.start()

   # wait until a song is prefetched (in case two 'gets' are called quickly
   # after another)
   while len(prefetch) == 0:
      pass

   return prefetch.pop()

# as the query can take fscking long, we prefetch one song
log.msg( 'prefetching random song...' )
prefetch = [findSong(1)]
log.msg( '... prefetched %r' % prefetch[0] )

