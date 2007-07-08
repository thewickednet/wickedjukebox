#!/usr/bin/python
# -*- coding: utf-8 -*-

from twisted.application import internet, service
from twisted.protocols import basic
from twisted.internet import protocol, reactor, defer
from twisted.python   import log
import os
from demon.wickedjukebox import Librarian
from demon.util import config
from demon.wickedjukebox import Channel
import demon.xmlrpc as xmlrpc

class Gatekeeper(object):
   """
   Responsible to route commands
   """

   channels = []
   lib = Librarian()
   activeChannel = None
   knownCommands = 'setChannel activeChannel rescanlib play pause next prev stop open close q exit quit bye currentSong'.split()

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
         else:
            del(channel)
      self.xmlrpcs = xmlrpc.Satellite()
      self.xmlrpcs.start()

   def stopThreads(self):
      self.lib.abortAll()
      for c in self.channels:
         c.close()
      self.xmlrpcs.stop()

   def route( self, line ):
      command = line.split()[0]
      try:
         args = line.split()[1:]
      except IndexError:
         args = None
      if args == []: args = None

      #
      # Rescanning the library
      #
      if command == 'rescanlib':
         return self.lib.rescanLib(args)

      #
      # Get Current Song
      #
      if command == 'currentSong':
         try:
            id = self.activeChannel.currentSong()
            return 'OK: %d' % id
         except:
            return 'ERR'

      #
      # Selecting a Channel
      #
      elif command == 'setChannel':
         if len(args) != 1:
            return "ER: setChannel only takes one argument (name of channel)!"
         channelFound = False
         for channel in self.channels:
            if channel.name == args[0]:
               channelFound = True
               self.activeChannel = channel
               self.xmlrpcs.setChannel( channel )
         if channelFound == False:
            channel = Channel( args[0] )
            if channel.name is None:
               del(channel)
               return "ER: no such channel!"
            self.channels.append( channel )
            self.activeChannel = self.channels[-1]
            self.xmlrpcs.setChannel( self.channels[-1] )
         return "OK: Selected channel %s" % self.activeChannel.name.encode('utf-8')

      #
      # Querying the active channel
      #
      elif command == 'activeChannel':
         if self.activeChannel is None:
            return "OK: %s" % self.activeChannel
         else:
            return "OK: %s" % self.activeChannel.name.encode('utf-8')

      #
      # Starting the active channel
      #
      elif command == 'open':
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

      #
      # Stopping the active channel
      #
      elif command == 'close':
         if self.activeChannel is not None:
            try:
               self.activeChannel.close()
               self.activeChannel.join()
               return "OK: %s closed" % self.activeChannel.name.encode('utf-8')
            except Exception, ex:
               return "ER: %s" % str(ex)
         return "ER: No channel selected! Either define one in the config file or use 'setChannel <cname>' first!"

      #
      # Start playing music
      #
      elif command == 'play':
         if self.activeChannel is not None:
            return self.activeChannel.startPlayback()
         return "ER: No channel selected! Either define one in the config file or use 'setChannel <cname>' first!"

      #
      # Stop playing music
      #
      elif command == 'stop':
         if self.activeChannel is not None:
            return self.activeChannel.stopPlayback()
         return "ER: No channel selected! Either define one in the config file or use 'setChannel <cname>' first!"

      #
      # Skip song
      #
      elif command == 'next':
         if self.activeChannel is not None:
            return self.activeChannel.skipSong()
         return "ER: No channel selected! Either define one in the config file or use 'setChannel <cname>' first!"

      else:
         return "ER: '%s' is an unknown command" % repr(command)


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
   gate     = None

   def __init__( self ):
      self.gate = Gatekeeper(self)

   def __repr__( self ):
      return "<WJBFactory>"

   def processLine( self, line ):
      if line == '': return defer.succeed( "ER: Unknown Command" )
      if line.split()[0] not in self.gate.knownCommands:
         return defer.succeed( "ER: Unknown Command" )
      else:
         return defer.succeed( self.gate.route( line ) )

   def stopFactory(self):
      self.gate.stopThreads()

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
   internet.TCPServer(int(config['demon.port']), factory).setServiceParent(
       service.IServiceCollection(application))
else:
   log.err( "Application failed to start up." )

