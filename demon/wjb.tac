#!/usr/bin/python
# -*- coding: utf-8 -*-

from twisted.application import internet, service
from twisted.protocols   import basic
from twisted.internet    import protocol, defer
from twisted.python      import log
from twisted.web         import server

import os
from demon.wickedjukebox import Librarian
from demon.util import config
from demon.wickedjukebox import Channel
from demon.xmlrpc import SatelliteAPI

gate = None

class Gatekeeper(object):
   """
   Responsible to route commands
   """

   channels = []
   lib = Librarian()
   activeChannel = None

   def __init__(self, factory):
      self.__factory = factory
      if config['demon.default_channel'] != '':
         channel = Channel( config['demon.default_channel'] )
         if channel.name is not None:
            log.msg( "Channel %s selected (from config.ini)" % channel.name )
            self.channels.append(channel)
            self.activeChannel = self.channels[-1]
            if config['demon.open_channel'] == '1':
               self.activeChannel.start()
            if config['demon.auto_play'] == '1':
               self.activeChannel.startPlayback()
         else:
            del(channel)

   def stopThreads(self):
      self.lib.abortAll()
      for c in self.channels:
         c.close()

   def do_doc(self, args):
      """
      Shows the available commands. Hopefully with some documentation.

      PARAMETERS
         [none]

      RETURNS
         This help text
      """
      lst = [ (f[3:], self.__getattribute__(f), self.__getattribute__(f).__doc__) for f in dir(self) if f.startswith('do_') ]
      lines = []
      for fname, func, doc in lst:
         if doc is None: doc = "[undocumented]"
         lines.append( "" )
         lines.append( "" )

         fparms = func.func_code.co_varnames[0:func.func_code.co_argcount]
         lines.append( "%s(%s)" % (fname, ', '.join(fparms) ) )

         for l in doc.split('\n'):
            lines.append( "   %s" % (l.replace('\n', '').strip() ) )

      return "%s\n === End of help ===" % '\n'.join(lines)

   def do_help(self, args):
      """
      Lists the available commands.

      PARAMETERS
         [none]

      RETURNS
         This help text
      """

      if args is not None and len(args) == 1:
         try:
            doc = self.__getattribute__("do_%s" % args[0]).__doc__
            doclines = [x.strip() for x in doc.split('\n')]
            lines = [
               79*"-",
               "Help on %s" % args[0],
               79*"-"
               ]
            for x in doclines:
               lines.append( x )
         except AttributeError:
            return "No such command!"
      else:
         lst = [ (f[3:], self.__getattribute__(f), self.__getattribute__(f).__doc__) for f in dir(self) if f.startswith('do_') ]
         lines = [
            "Available commands",
            79*"-"
            ]
         for fname, func, doc in lst:
            if doc is None: doc = "[undocumented]"
            else:
               doclines = [x.strip() for x in doc.split('\n')]
               for x in doclines:
                  if x != '':
                     doc = x
                     break

            lines.append( "%-30s : %s" % (fname, doc) )

      return "%s\n === End of help ===" % '\n'.join(lines)

   do_h = do_help # alias

   def do_quit(self, args):
      """
      Closes the remote connection

      PARAMETERS
         [none]

      RETURNS
         the text string "bye"
      """

      return "bye"

   do_q = do_quit # alias

   def do_play(self, args=None):
      """
      Starts music playback

      PARAMETERS
         [none]

      RETURNS
         "OK" on success
         "ER: <msg>" on error
      """

      if self.activeChannel is not None:
         return self.activeChannel.startPlayback()
      return "ER: No channel selected! Either define one in the config file or use 'setChannel <cname>' first!"

   def do_enqueue(self, args):
      """
      Enqueues a song

      PARAMETERS
         $1: The song ID
         $2: The user ID
      """
      if len(args) < 2:
         return 'ER: 2 arguments required. Consult the help!'
      if self.activeChannel is not None:
         return self.activeChannel.enqueue(int(args[0]), int(args[1]))
      return "ER: No channel selected! Either define one in the config file or use 'setChannel <cname>' first!"


   def do_rescanlib(self, args=None):
      """
      Starts a rescan of the library

      PARAMETERS
         $1 - force a scan even if the file has not been changed on disk since
              last scan (boolean)

         $2 - The "cap" string. Example: "rescanlib Th" only rescans file
              matching "Th*". Note that this caping only applies to the top
              level.

      RETURNS
         "OK" - This always returns OK, as all the command does is start a new
                thread in the background. Possible errors that happen in this
                thread are unknown at the time this command is executed.
      """

      return self.lib.rescanLib(args)

   def do_currentSong(self, args=None):
      """
      Retrieves the id of the current song

      PARAMETERS
         [none]

      RETURNS
         "OK: <id>" on success
         "ER" on error
      """

      try:
         id = self.activeChannel.currentSong()
         return 'OK: %d' % id
      except:
         return 'ER'

   def do_setChannel(self, args=None):
      """
      Selectis a channel. Forthcoming commands will be targeted applied to that
      channel.

      PARAMETERS
         $1 - the name of the channel

      RETURNS
         "ER: <msg>" on error
         "OK: <msg>" on success
      """

      if len(args) != 1:
         return "ER: setChannel only takes one argument (name of channel)!"

      channelFound = False
      for channel in self.channels:
         if channel.name == args[0]:
            channelFound = True
            self.activeChannel = channel

      if channelFound == False:
         channel = Channel( args[0] )
         if channel.name is None:
            del(channel)
            return "ER: no such channel!"
         self.channels.append( channel )
         self.activeChannel = self.channels[-1]

      return "OK: Selected channel %s" % self.activeChannel.name.encode('utf-8')

   def getChannelByID(self, channelID):
      """
      Returns a channel by id from the known channel-list

      @type  channelID: int
      @param channelID: the channel-id
      """

      for chan in self.channels:
         if chan.dbModel.id == channelID:
            return chan

   def do_activeChannel(self, args=None):
      """
      Displays the name of the currently selected channel

      PARAMETERS
         [none]

      RETURNS
         "OK: <msg>" on success
      """

      if self.activeChannel is None:
         return "OK: %s" % self.activeChannel
      else:
         return "OK: %s" % self.activeChannel.name.encode('utf-8')

   def do_open(self, args=None):
      """
      Activates/Starts the currently selected channel.

      PARAMETERS
         [none]

      RETURNS
         "OK: <msg>" on success
         "ER: <msg>" on error
      """

      if self.activeChannel is not None:
         try:
            if self.activeChannel.isStopped():
               n = self.activeChannel.name
               self.channels.remove(self.activeChannel)
               self.activeChannel = None
               self.channels.append( Channel(n) )
               self.activeChannel = self.channels[-1]
               del(n)
            self.activeChannel.open()
            return "OK: %s opened" % self.activeChannel.name.encode('utf-8')
         except Exception, ex:
            return "ER: %s" % str(ex)
      return "ER: No channel selected! Either define one in the config file or use 'setChannel <cname>' first!"

   def do_close(self, args=None):
      """
      Deactivates/Stops the currently selected channel.

      PARAMETERS
         [none]

      RETURNS
         "OK: <msg>" on success
         "ER: <msg>" on error
      """

      if self.activeChannel is not None:
         try:
            self.activeChannel.close()
            self.activeChannel.join()
            return "OK: %s closed" % self.activeChannel.name.encode('utf-8')
         except Exception, ex:
            return "ER: %s" % str(ex)
      return "ER: No channel selected! Either define one in the config file or use 'setChannel <cname>' first!"

   def do_stop(self, args=None):
      """
      Stops music playback

      PARAMETERS
         [none]

      RETURNS
         "OK" on success
         "ER: <msg>" on error
      """

      if self.activeChannel is not None:
         return self.activeChannel.stopPlayback()
      return "ER: No channel selected! Either define one in the config file or use 'setChannel <cname>' first!"

   def do_next(self, args=None):
      """
      Skips a song

      PARAMETERS
         [none]

      RETURNS
         "OK" on success
         "ER: <msg>" on error
      """

      if self.activeChannel is not None:
         return self.activeChannel.skipSong()
      return "ER: No channel selected! Either define one in the config file or use 'setChannel <cname>' first!"

   def do_moveup(self, args=None):
      """
      Moves a song up the queue by <n> steps

      PARAMETERS
         $1 - queue-id
         $2 - the "n" in steps
      """

      if self.activeChannel is not None:
         return self.activeChannel.moveup(int(args[0]), int(args[1]))
      return "ER: No channel selected! Either define one in the config file or use 'setChannel <cname>' first!"

   def do_movedown(self, args=None):
      pass

   def do_movetop(self, args=None):
      pass

   def do_movebottom(self, args=None):
      pass

   def do_enqueue_album(self, args=None):
      pass

   def do_queue_delete(self, args=None):
      pass

   def do_queue_clear(self, args=None):
      pass


class WJBProtocol(basic.LineReceiver):

   def connectionMade(self):
      self.transport.write("No rest for the wicked.\r\n")

   def lineReceived( self, line ):
      log.msg( "<", line )
      if line in 'q bye exit quit'.split(): self.transport.loseConnection()
      self.factory.processLine(line
            ).addErrback( lambda _: self.transport.write("Internal server error\r\n")
            ).addCallback( lambda m:
                      self.transport.write("%s\r\n" % m))

   def disconnect(self):
      self.transport.loseConnection()

class WJBFactory( protocol.ServerFactory ):

   protocol = WJBProtocol

   def __init__( self ):
      global gate
      gate = Gatekeeper(self)

   def __repr__( self ):
      return "<WJBFactory>"

   def gateCall(self, line):
      global gate
      command = line.split()[0]
      try:
         args = line.split()[1:]
      except IndexError:
         args = None
      if args == []: args = None

      # call a function on the gatekeeper object matching do_<command>(args)
      try:
         funcname = "do_%s" % command
         f = gate.__getattribute__( funcname )
         return f(args)
      except AttributeError, ex:
         return "ER: Unable to execute %s: %s" % (repr(command), str(ex))
      except Exception, ex:
         return "ER: Unexpected error when executing %s: %s" % (repr(command), str(ex))


   def processLine( self, line ):
      global gate
      if line == '': return defer.succeed( "ER: Unknown Command" )
      return defer.succeed( self.gateCall( line ) )

   def stopFactory(self):
      global gate
      gate.stopThreads()

application = None
if os.getuid() == 0:
   log.err( "WARNING: Process started as root. Trying to change to a less priviledged user..." )
   try:
      application = service.Application('wickedjukebox', uid=1, gid=1)
   except:
      log.err( "... failed to switch user." )
      if config['core.allow_root_exec'] == 1:
         log.err( "Running as superuser instead. THIS IS DANGEROUS! To disable this behaviour, set 'allow_root_exec' to 0 in config.ini" )
         application = service.Application('wickedjukebox')
else:
   application = service.Application('wickedjukebox')

if application is not None:
   factory = WJBFactory()
   internet.TCPServer( int(config['demon.port']), factory).setServiceParent(
       service.IServiceCollection(application))
   sapi = SatelliteAPI()
   sapi.setGate( gate )
   if config['xmlrpc.port'] != '':
      log.msg( '%-20s %30s' % ( 'XML-RPC support:', 'enabled' ) )
      internet.TCPServer( int(config['xmlrpc.port']), server.Site(sapi)).setServiceParent(
          service.IServiceCollection(application))
   else:
      log.msg( '%-20s %20s %s' % ( 'XML-RPC support:', 'disabled', '(no port specified)' ) )
else:
   log.err( "Application failed to start up." )

