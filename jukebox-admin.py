#!/var/www/wicked.lu/jukebox_env_2009/environment/bin/python
# -*- coding: utf8 -*-
import cmd
from os import path
import sys; sys.path.insert(1, 'pydata')
import lastfm
from demon.dbmodel import Setting, \
                        Session, \
                        Artist, \
                        genreTable, \
                        songTable, \
                        albumTable, \
                        artistTable, \
                        usersTable, \
                        song_has_genre, \
                        settingTable
from sqlalchemy.sql import func, select, update, insert
from util import direxists
import logging
import logging.config
logging.config.fileConfig("logging.ini")

LOG = logging.getLogger(__name__)

def get_artists(glob="*"):
   if glob == "": glob = "*"
   glob = glob.replace("*", "%")
   s = select([artistTable],
         artistTable.c.name.like(glob),
      order_by=["name"]
      )
   r = s.execute()
   return r.fetchall()

def get_albums(aname, glob="*"):
   if glob == "": glob = "*"
   glob = glob.replace("*", "%")
   s = select([albumTable])
   s = s.where( artistTable.c.name == aname )
   s = s.where( albumTable.c.artist_id == artistTable.c.id )
   s = s.where( albumTable.c.name.like(glob) )
   s = s.order_by( "name" )
   r = s.execute()
   return r.fetchall()

def get_songs(bname, glob):
   if glob == "": glob = "*"
   glob = glob.replace("*", "%")
   s = select([songTable])
   s = s.where( albumTable.c.name == bname )
   s = s.where( songTable.c.album_id == albumTable.c.id )
   s = s.where( songTable.c.title.like(glob) )
   s = s.order_by( "title" )
   r = s.execute()
   return r.fetchall()

class Console(cmd.Cmd):

   __ctx_artist = "unset"
   __ctx_album  = "unset"
   __path       = []

   def __init__(self):
      "Bootstrap the command line interpreter"
      cmd.Cmd.__init__(self)
      self.set_promt()

   def listSettings( self, channel_id=None, user_id=None ):
      """
      List settings

      @param channel_id: If set, list only settings for that channel
      @param user_id: If set, list only settings for that user
      """
      sel = settingTable.select()

      if channel_id:
         sel = sel.where( settingTable.c.channel_id == int(channel_id) )

      if user_id:
         sel = sel.where( settingTable.c.user_id == int(user_id) )

      sel = sel.order_by( "user_id", "channel_id", "var" )
      print " Channel ID | User ID | Setting                   | Value"
      previous_channel = None
      for row in sel.execute().fetchall():
         if row["channel_id"] != previous_channel:
            print "---------+------------+---------------------------+----------------"
            previous_channel = row['channel_id']
         print " %10d | %7d | %-25s | %s" % ( 
               row["channel_id"],
               row["user_id"],
               row["var"],
               row["value"],
               )

   def emptyline(self):
      """Do nothing on empty input line"""
      pass

   def set_promt(self):
      "Sets the default prompt"
      if len(self.__path) == 0:
         self.prompt = "---\njukebox> "
      else:
         self.prompt = "---\n%s> " % "/".join(self.__path)

   def get_string(self, string):
      "If a string is enclosed with quotes, remove them and return the proper string"
      if string == "": return string
      # remove quotes
      if string[0] in ['"', "'"]:
         string = string[1:-1]
      return string

   def do_quit(self, line):
      """Quits you out of Quitter."""
      print "bye"
      return 1

   def do_rescan(self, line, force = 0):
      """
      Scan the defined library folders for new songs.

      SYNOPSIS
         newscan [capping]

      PARAMETERS
         capping  - [optional] Only scan folders that start with the string <capping>

      EXAMPLES
         jukebox> newscan
         jukebox> newscan Depeche
      """
      mediadirs = [ x for x in Setting.get('mediadir').split(' ') if direxists(x) ]
      import scanner
      scanner.scan( mediadirs[0], unicode(line) )

      print "done"

   def do_update_tags(self, line):
      """
      Updates song tags via Last.FM

      To avoid hammering the Lasst.FM API we will add a small sleep between
      function call, so this may take a long time!

      SYNOPSIS
         update_tags <artist>

      PARAMETERS
         artist - The artis name
      """
      sess = Session()
      api_key = Setting.get( "lastfm_api_key", None )
      if not api_key:
         print "ERROR: No API key specified. You can do this it in the settings"
         return
      api = lastfm.Api( api_key )
      artist = sess.query(Artist).filter_by( name=unicode(line) ).first()
      if not artist:
         sess.close()
         print "Artist %r not found" % line
         return
      songs = artist.songs
      print "%5d songs to update" % len(songs)
      from time import sleep
      for song in songs:
         song.update_tags(api)
         sleep(1)
         print "%-40s has now %4d tags" % (song.title, len(song.tags))

      sess.close()


   def do_orphans(self, line):
      """
      Find files that are in the database but not on disk
      """

      s = select([songTable.c.id, songTable.c.localpath])
      s = s.order_by( "localpath" )
      r = s.execute()
      for row in r:
         if not path.exists( row[1] ):
            print "%10d %s" % (row[0], row[1])

   def do_genres(self, line):
      """
      Lists genres stored in the DB

      SYNOPSIS
         genres [order]

      PARAMETERS
         order  - may be one of "name" or "count". If ommitted, "count" is
                  used.
      """

      if line == "count" or line == "":
         order_by = "song_count"
      elif line == "name":
         order_by = "name"

      s = select([genreTable.c.id, genreTable.c.name,
         func.count(song_has_genre.c.song_id).label('song_count')],
         genreTable.c.id==song_has_genre.c.genre_id,
         group_by=genreTable.c.id,
         order_by=order_by
         )
      r = s.execute()

      print " id   | Genre                          | count "
      print "------+--------------------------------+-------"
      for g in r.fetchall():
         print "%5d | %-30s | %d" % (g.id, g.name, g.song_count)
      print "------+--------------------------------+-------"
      print " id   | Genre                          | count "

   def do_merge_genre(self, line):
      """
      Moves genre A into genre B (only B remains!)

      SYNOPSIS
         merge_genre A B

      PARAMETERS
         Both "A" and "B" are id's to genres in the database. Use "genres" to
         get a list
      """
      try:
         old_genre, new_genre = line.split(" ")
      except Exception, ex:
         print str(ex)
         return

      old_genre = int(old_genre)
      new_genre = int(new_genre)
      u = song_has_genre.update(
               song_has_genre.c.genre_id==bindparam("a"),
               values = {'genre_id': bindparam("b")}
            )
      u.execute(a=old_genre, b=new_genre)

   def do_genre_songs(self, line):
      """
      Lists songs of a given genre

      SYNOPSIS
         genre_songs <genre_id>
      """
      genre_id = int(line)
      s = select([
               songTable.c.id,
               artistTable.c.name.label("aname"),
               albumTable.c.name.label("bname"),
               songTable.c.title
            ],
            and_(
               songTable.c.id            == song_has_genre.c.song_id,
               song_has_genre.c.genre_id == genre_id,
               songTable.c.artist_id     == artistTable.c.id,
               songTable.c.album_id      == albumTable.c.id
               ),
            order_by=["aname", "bname", "title"]
            )
      r = s.execute()
      for s in r.fetchall():
         aname = s.aname is not None and s.aname.encode("utf-8") or "None"
         bname = s.bname is not None and s.bname.encode("utf-8") or "None"
         title = s.title is not None and s.title.encode("utf-8") or "None"
         print "%5d | %-30s | %-30s | %-30s" % (s.id, aname, bname, title)

   def do_rename_genre(self, line):
      """
      Renames a genre

      SYNOPSIS
         rename_genre <genre_id> <new_name>
      """

      try:
         args = line.split(" ")
         gid = int(args[0])
         name = " ".join(args[1:])
         name = self.get_string(name)
      except Exception, ex:
         print str(ex)
         return

      u = genreTable.update(
               genreTable.c.id==bindparam("gid"),
               values = {'name': bindparam("name")}
            )
      u.execute(gid=gid, name=name)

   def do_find_duplicates(self, line):
      """
      Finds duplicates based on artist/track name.

      SYNOPSIS
         find_duplicates [log_file]

      PARAMETERS
         log_file -- path to a log file
      """

      hashtable = {}
      logfile = None
      default_out = sys.stdout
      if line != '':
         try:
            if path.exists(line):
               print "File %s exists" % line
               return
            logfile = open(line, 'w')
            sys.stdout = logfile
         except IOError:
            print "Unable to open %r" % line
            return

      s = select([
            songTable.c.id,
            songTable.c.localpath,
            songTable.c.title,
            artistTable.c.name
         ],
         songTable.c.artist_id == artistTable.c.id
      )

      result = s.execute().fetchall()

      for row in result:
         key = "%s - %s" % (row[3], row[2])
         if key in hashtable:
            hashtable[key].append(row[1])
         else:
            hashtable[key] = [ row[1] ]

      for key in hashtable:
         if len(hashtable[key]) == 1:
            continue

         print "key: %r" % key
         for localpath in hashtable[key]:
            print "   %r" % localpath
         print 80*"-"
      sys.stdout = default_out

   def do_cd(self, line):
      """
      Changes context. Three levels possible: Root -> Artist -> Album

      SYNOPSIS
         cd <path>

      PARAMETERS
         path    - name of the artist/album or ".."
      """
      arg = self.get_string(line)

      if arg.strip() == "..":
         try:
            parent = self.__path.pop()
         except:
            pass
         self.set_promt()
         return

      if len(self.__path) == 2:
         return

      self.__path.append( arg )
      self.set_promt()

   def do_ls(self, line):
      "Lists entries in the current context"
      glob = self.get_string(line)
      if len(self.__path) == 0:
         artists = get_artists(glob)
         for a in artists:
            if a.name is None: continue
            print a.name.encode("utf-8")
      elif len(self.__path) == 1:
         albums = get_albums( self.__path[-1], glob )
         for b in albums:
            if b.name is None: continue
            print b.name.encode("utf-8")
      elif len(self.__path) == 2:
         songs = get_songs( self.__path[-1], glob )
         for s in songs:
            if s.title is None: continue
            print s.title.encode("utf-8")

   def do_online_users(self, line):
      "Lists users currently online in the web interface"
      s = select([usersTable],
            func.addtime( usersTable.c.proof_of_life, '0:03:00' ) > func.now(),
         )
      r = s.execute()
      for row in r.fetchall():
         print row

   def do_settings(self, line):
      """
      Lists or set application settings

      SYNOPSIS
         settings [channel_id [user_id [setting value]]]

      PARAMETERS
         channel_id - if specified, list only settings of that channel
         user_id    - if specified, list only settings for that user (and channel)
         setting    - the setting name (when modifying the setting)
         value      - if specified, change that setting
      """

      params = line.split()
      if len(params) <= 2:
         self.listSettings( *params )
         return

      channel_id, user_id, var, value = params
      testsel = select( [settingTable.c.value] )
      testsel = testsel.where( settingTable.c.channel_id == int(channel_id) )
      testsel = testsel.where( settingTable.c.user_id == int(user_id) )
      testsel = testsel.where( settingTable.c.var == var )
      res = testsel.execute()
      if res and res.fetchone():
         # we already have the setting. Go and update it
         upq = update( settingTable )
         upq = upq.where( settingTable.c.channel_id == int(channel_id) )
         upq = upq.where( settingTable.c.user_id == int(user_id) )
         upq = upq.where( settingTable.c.var == var )
         upq = upq.values( { "value": value } )
         upq.execute()
      else:
         # new setting -> insert
         insq = insert( settingTable )
         insq = insq.values( {
            "channel_id": int(channel_id),
            "user_id": int(user_id),
            "var": var,
            "value": value
            } )
         insq.execute()
      LOG.debug( "New setting stored: %r" % params )

   do_exit = do_quit
   do_q    = do_quit
   do_EOF  = do_quit

if __name__ == '__main__':
   app = Console()
   app.cmdloop()
