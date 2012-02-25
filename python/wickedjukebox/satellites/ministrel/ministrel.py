import xmlrpclib
import simplejson
from config import config
import time

def unmarshal( data ):
   return simplejson.loads( data )

if __name__ == "__main__":

   print "Starting up... Hit CTRL+C to stop polling"
   try:
      while True:
         server = xmlrpclib.Server('http://%(host)s:%(port)s' % config)
         songid = unmarshal( server.getCurrentSong( int(config['channel'])) )
         songdata = unmarshal (server.getSongData( songid ) )
         fp = open( 'songdata.txt', 'w' )
         fp.write( "%(artist)s - %(title)s" % songdata )
         fp.close()
         time.sleep( config['interval'] )
   except KeyboardInterrupt:
      print "bye\n"


