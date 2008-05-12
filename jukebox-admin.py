#!/usr/bin/python
import cmd
from os import path
from demon.model import getSetting
from demon.wickedjukebox import Scanner, fs_encoding, direxists

class Console(cmd.Cmd):

   __scanner = None

   def __init__(self):
      cmd.Cmd.__init__(self)
      self.prompt = "jukebox> "

   def do_quit(self, line):
      """Quits you out of Quitter."""
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
      """Rescans the media folders

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

if __name__ == '__main__':
   app = Console()
   app.cmdloop()
