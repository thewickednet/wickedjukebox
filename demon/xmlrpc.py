# -*- coding: utf-8 -*-
import SimpleXMLRPCServer
from model import create_session, getSetting, Artist, Album, Song
from sqlalchemy import and_
import simplejson, threading
from twisted.python import log

def marshal(str):
   return simplejson.dumps( str )

class SatelliteAPI:

   channel = None

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

   def run(self):

      self.keepRunning = True
      port = getSetting( 'xmlrpc_port' )
      if port == '':
         log.msg( "No port specified for XML-RPC. Disabling support!" )
         return

      ip   = getSetting( 'xmlrpc_iface', '127.0.0.1' )
      self.server = SimpleXMLRPCServer.SimpleXMLRPCServer((ip, port))
      self.server.register_instance(SatelliteAPI())
      log.msg( "Serving XMLRPC on port %s" % port )
      try:
         while self.keepRunning:
            self.server.handle_request()
      except:
         log.msg( 'Error in XMLRPC' )

   def setChannel(self, channel):
      self.server.channel = channel

   def stop(self):
      log.msg( 'XMLRPC service stopped' )
      self.keepRunning = False
