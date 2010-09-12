"""
This is a no-op playmode used as blueprint for new playmodes.
Simply complete the methods in this module and make them return the right type
and you should be fine.
"""

from demon.plparser import parseQuery, ParserSyntaxError
from demon.dbmodel import Session, dynamicPLTable, Setting, Song, usersTable, \
                          channelTable, engine, songTable, songStandingTable, \
                          channelSongs
from sqlalchemy.sql import text as dbText, func, select, or_
from demon.util import config
import threading

import logging
LOG = logging.getLogger(__name__)

def bootstrap(channel_id):
   """
   This is always called as soon as the module is loaded.
   It is used to bootstrap the module.

   Note that this will be called on each iteration, so it should cope with
   that. If you want to process this method only one you should deal with that
   internally (by using a sentinel variable for example).

   @param channel_id: The channel ID
   """
   pass

def get(channel_id):
   """
   Returns a random song.
   @param channel_id: The channel ID for which we are returning results
   @note: This method should *always* return a valid Song instance. Only
          return "None" if something seriously went wrong.

   @rtype:  None | Song
   @return: Either "None" if no random song could be determined,
            or a "Song" instance (as imported from demon.model --> see above)
   """

   candidates = fetch_candidates( channel_id )
   if not candidates:
      LOG.warning( "No song returned!" )
      return
   sess = Session()
   song = sess.query(Song).filter(songTable.c.id == candidates[0][0] ).first()
   sess.close()
   return song

def peek(channel_id):
   """
   Returns the song that will play immediately after the current song
   @param channel_id: The channel ID for which we are returning results
   @note: Returns "None" if the playmode does not support this feature
   @rtype:  None | Song
   @return: Either "None" if the upcoming song cannot be determined
            or a "Song" instance (as imported from demon.model --> see above)
   """
   return None

def prefetch(channel_id, async=True):
   """
   Trigger prefetching of a song. This may be used when a client requests that
   the song marked as "upcoming song" is unwanted.

   Playmodes that do not support a lookahead (see also "peek") will simply do
   nothing when this method is called.
   @param channel_id: The channel ID for which we are returning results
   @param async: Whether to run the internal prefetch call asynchronously or
                 not. This MUST be implemented for asynchronous prefetchers to
                 ensure thread safety
   """
   pass

def fetch_candidates( channel_id ):
   try:
      # get settings
      userRating  = int(Setting.get('scoring_userRating',   4,  channel_id=channel_id))
      lastPlayed  = int(Setting.get('scoring_lastPlayed',   10, channel_id=channel_id))
      songAge     = int(Setting.get('scoring_songAge',      1,  channel_id=channel_id))
      neverPlayed = int(Setting.get('scoring_neverPlayed',  4,  channel_id=channel_id))
      randomness  = int(Setting.get('scoring_randomness',   1,  channel_id=channel_id))
      recency_threshold = int( Setting.get('recency_threshold', 120, channel_id=channel_id))
      max_random_duration = int(Setting.get('max_random_duration', 600,  channel_id=channel_id))
      proofoflife_timeout = int(Setting.get('proofoflife_timeout', 120))

      # look who's online
      listeners_query = select([usersTable.c.id,
                  usersTable.c.username],
            func.unix_timestamp(usersTable.c.proof_of_listening) \
                  + proofoflife_timeout \
                  > func.unix_timestamp(func.now()))
      LOG.debug( listeners_query )
      r = listeners_query.execute()
      online_users = [ row[0] for row in r ]
      LOG.debug( "The following users are online: %r" % online_users )

      # first, we fetch a limited number of songs using the basic stats. This will
      # prevent too many queries when determining love/hate stats.
      rough_query = select( [
            songTable.c.id,
            songTable.c.duration,
            channelSongs.c.lastPlayed
         ],
         from_obj=[
            songTable.outerjoin( channelSongs, songTable.c.id == channelSongs.c.song_id )
         ] )

      # skip songs that are too long
      rough_query = rough_query.where( songTable.c.duration < max_random_duration )

      # skip songs that have been recently played
      from datetime import datetime, timedelta
      delta = timedelta( minutes=recency_threshold )
      old_time = datetime.now() - delta
      rough_query = rough_query.where( or_(
         channelSongs.c.lastPlayed < old_time,
         channelSongs.c.lastPlayed == None))

      # bring in some random
      rough_query = rough_query.order_by( func.rand() )

      # now keep only a selected few
      rough_query = rough_query.limit(200)
      LOG.debug( rough_query )

      results = []
      count_added = 0
      for row in rough_query.execute():
         # if the song is hated by someone, don't consider it further
         hate_query = select( [songStandingTable.c.user_id] )
         hate_query = hate_query.where( songStandingTable.c.user_id.in_(online_users) )
         hate_query = hate_query.where( songStandingTable.c.standing=='hate' )
         hate_query = hate_query.where( songStandingTable.c.song_id == row[0] )
         a = hate_query.alias()
         hate_count = a.count().execute().fetchone()[0]
         if hate_count > 0:
            continue

         # count the loves, for points calculation
         love_query = select( [songStandingTable.c.user_id] )
         love_query = love_query.where( songStandingTable.c.user_id.in_(online_users) )
         love_query = love_query.where( songStandingTable.c.standing=='love' )
         love_query = love_query.where( songStandingTable.c.song_id == row[0] )
         a = love_query.alias()
         love_count = a.count().execute().fetchone()[0]

         # okay... let's do the scoring, first, zero in:
         score = 0.0
         # now, promote loved songs
         if len( online_users ):
            score = score + (userRating * (love_count / len(online_users)))
         # give songs that have never been played a fair chance too:
         if not row[2]:
            score = score + neverPlayed

         # construct a string representation of the recency of the song.
         # using the number of minutes since it's last played. If it hasn't,
         # we'll assume 1. jan. 1900.
         # We then zero-pad this, reverse the string and prefix the score. This
         # will give us a usable sort key to sort by score descending, then by
         # recency ascending.
         delta = datetime.now() - (row[2] and row[2] or datetime( 1900, 01, 01 ))
         num_delta = "%08d" % (delta.days*24*60 + delta.seconds/60)
         # num_delta = num_delta[::-1] # reverses the string
         key_score = "%05.2f" % score
         key_score = key_score.replace( ".", "" )
         sortkey="%s%s" % (key_score, num_delta)
         results.append( (row[0],
               { "score": score,
                 "love_count": love_count,
                 "duration": row[1],
                 "last_played": row[2],
                 "sortkey": sortkey}))
         count_added += 1
         if count_added == 10:
            break

      results.sort( cmp = lambda x, y: cmp( float(y[1]["sortkey"]), float(x[1]["sortkey"]) ) )
      return results

   except Exception, e:
      from  traceback import format_exc
      LOG.critical(format_exc() )

def test(channel_id):
   """
   Used to run a test on the random mode.This should return a list o tuples
   containing a Song instance as first element, and a dictionary of stats as
   second element.
   @param channel_id: The channel ID for which we are returning results
   @return: List of 2-tuples (Song, stats)
   """
   candidates = fetch_candidates( channel_id )
   return candidates[0:10]

