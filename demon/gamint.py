#!/usr/bin/python
import gamin, time, threading
from os.path import join, abspath, isdir

class Monitor( threading.Thread ):

   __monitors = []

   def __init__(self, root):
      self.__root = abspath( root )
      print "monitoring %s" % root
      threading.Thread.__init__(self)

   def event_fired( self, relpath, event ):
      if event == gamin.GAMCreated:
         if isdir( join(self.__root, relpath )):
            self.__monitors.append( Monitor( join( self.__root, relpath ) ) )
            self.__monitors[-1].start()
         else:
            print self.getName(), relpath, event
      elif event == gamin.GAMExists:
         if relpath != self.__root:
            if isdir( join(self.__root, relpath )):
               self.__monitors.append( Monitor( join( self.__root, relpath ) ) )
               self.__monitors[-1].start()
         else:
            print self.getName(), relpath, event
      else:
         print self.getName(), relpath, event

   def run(self):
      self.__mon = gamin.WatchMonitor()
      self.__mon.watch_directory( self.__root, self.event_fired )
      while True:
         if self.__mon.event_pending() > 0:
            self.__mon.handle_events()
         time.sleep(1)

if __name__ == '__main__':

   m = Monitor( 'data' )
   m.start()

