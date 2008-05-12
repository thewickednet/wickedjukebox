#!/usr/bin/python
import cmd
from os import path
from demon.model import getSetting, \
                        genreTable, \
                        songTable, \
                        albumTable, \
                        artistTable, \
                        song_has_genre, \
                        create_session
from sqlalchemy import func, select, bindparam, and_
from demon.wickedjukebox import Scanner, fs_encoding, direxists

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
   s = select([albumTable],
         and_(artistTable.c.name == aname, albumTable.c.artist_id == artistTable.c.id, albumTable.c.name.like(glob)),
         order_by=[albumTable.c.name]
      )
   r = s.execute()
   return r.fetchall()

def get_songs(bname, glob):
   if glob == "": glob = "*"
   glob = glob.replace("*", "%")
   s = select([songTable],
         and_( albumTable.c.name == bname, songTable.c.album_id == albumTable.c.id, songTable.c.title.like(glob) ),
         order_by=["title"]
      )
   r = s.execute()
   return r.fetchall()

class Console(cmd.Cmd):

   __scanner = None
   __ctx_artist = "unset"
   __ctx_album  = "unset"
   __path       = []

   def __init__(self):
      cmd.Cmd.__init__(self)
      self.__sess = create_session()
      self.set_promt()

   def set_promt(self):
      if len(self.__path) == 0:
         self.prompt = "---\njukebox> "
      else:
         self.prompt = "---\n%s> " % "/".join(self.__path)

   def get_string(self, string):
      if string == "": return string
      # remove quotes
      if string[0] in ['"', "'"]:
         string = string[1:-1]
      return string

   def do_quit(self, line):
      """Quits you out of Quitter."""
      self.__sess.flush()
      self.__sess.close()
      print "bye"
      return 1

   do_exit = do_quit
   do_q    = do_quit
   do_EOF  = do_quit

   def cb(self):
      print "done scanning\n", self.__scanner.get_status()

   def emptyline(self):
      """Do nothing on empty input line"""
      pass

   def do_rescan(self, line, force = 0):
      """
      Rescans the media folders

      SYNOPSIS
         rescan [capping]

      PARAMETERS
         capping  - [optional] Only scan folders that start with the string <capping>

      EXAMPLES
         jukebox> rescan
         jukebox> rescan Depeche
      """

      mediadirs = [ x for x in getSetting('mediadir').split(' ') if direxists(x) ]

      if self.__scanner is not None and self.__scanner.isAlive():
         print "ERROR: another scan process is running!"

      self.__scanner = Scanner( mediadirs, [ force, line ] )
      self.__scanner.add_callback( self.cb )
      self.__scanner.start()
      print "job started. You may inspect the status with scan_status!"

   def do_force_scan(self, line):
      """Rescans the media folders, including files that have not changed since
last scan!  For a more detailed description see "help rescan"

SYNOPSIS
   force_scan [capping]
"""

      self.do_rescan( line, force=1 )

   def do_scan_status(self, line):
      """Shows the status of the current file scan"""
      print self.__scanner.get_status()

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
         print "%5d | %-30s | %-30s | %-30s" % (s.id, s.aname.encode("utf-8"), s.bname.encode("utf-8"), s.title.encode("utf-8"))

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

if __name__ == '__main__':
   app = Console()
   app.cmdloop()
