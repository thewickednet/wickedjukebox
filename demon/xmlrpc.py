# -*- coding: utf-8 -*-
import SimpleXMLRPCServer, threading
from model import create_session, getSetting, Artist, Album, Song
from sqlalchemy import and_
from twisted.python import log

try:
   import simplejson
   jsonEnabled = False
except:
   jsonEnabled = False

def marshal(data):
   if jsonEnabled:
      return simplejson.dumps( data )
   else:
      return data

class SatelliteAPI:

   channel = None

   def __init__(self, channel):
      self.channel = channel

   def get_albums(self, artistName):
      sess = create_session()
      artist = sess.query(Artist).selectfirst_by(Artist.c.name==artistName)

      if artist is not None:
         output = [ (x.id, x.name) for x in artist.albums ]

      sess.close()
      return marshal(output)

   def get_album_songs( self, albumID ):
      sess = create_session()
      album = sess.query(Album).selectfirst_by(Album.c.id == albumID)
      output = [ (a.id, a.title) for a in album.songs ]
      sess.close()
      return marshal(output)

   def ping(self):
      return marshal(True)

   def getCurrentSong(self):
      if self.channel is not None:
         return marshal(self.channel.currentSong())

   def getSongData(self, songID):
      sess = create_session()
      song = sess.query(Song).selectfirst_by(Song.c.id == songID )
      output = None
      if song is not None:
         output = {
            'artist': song.artist.name,
            'album': song.album.name,
            'title': song.title
         }
      sess.close()
      return marshal(output)

   def get_songs(self, artist=None, artistID=None, album=None, albumID=None):
      sess = create_session()

      if artistID is not None:
         dbArtist = sess.query(Artist).selectfirst_by(Artist.c.id == artistID )
      elif artist is not None:
         dbArtist = sess.query(Artist).selectfirst_by(Artist.c.name==artistName)

      if albumID is not None:
         dbAlbum = sess.query(Album).selectfirst_by(Album.c.id == albumID )
      elif album is not None:
         dbAlbum = sess.query(Album).selectfirst_by(
               and_(Album.c.name == album, Album.c.artist_id == dbArtist.id ) )

      output = [ dbArtist.name, dbAlbum.name ]
      sess.close()
      return marshal(output)

class Satellite(threading.Thread):

   def __init__(self, channel):
      self.port = getSetting( 'xmlrpc_port' )
      self.keepRunning = True
      if self.port == '':
         log.msg( '%-20s %20s %s' % ( 'XML-RPC support:', 'disabled', '(no port specified)' ) )
         self.keepRunning = False
         threading.Thread.__init__(self)
         return
      log.msg( '%-20s %30s' % ( 'XML-RPC support:', 'enabled' ) )

      self.ip   = getSetting( 'xmlrpc_iface', '127.0.0.1' )

      log.msg( "XML-RPC service starting up..." )
      while True:
         try:
            self.server = SimpleXMLRPCServer.SimpleXMLRPCServer((self.ip, int(self.port)))
            log.msg( '... done' )
            break;
         except:
            import time
            log.msg( "Retrying..." )
            time.sleep(1)
            pass

      self.server.register_instance(SatelliteAPI(channel))
      log.msg( "Serving XMLRPC on port %s" % self.port )
      threading.Thread.__init__(self)

   def run(self):

      try:
         while self.keepRunning:
            self.server.handle_request()
      except:
         log.msg( 'Error in XMLRPC' )

   def stop(self):
      if self.keepRunning == False:
         return
      log.msg( 'XMLRPC service stopped' )
      self.keepRunning = False

      # send a bogus request to the server, as the "handle_request" method is
      # blocking. So it it still there waiting for a final request.
      import xmlrpclib
      s = xmlrpclib.Server('http://%s:%s' % (self.ip, self.port))
      s.ping()
