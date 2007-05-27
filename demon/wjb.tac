#!/usr/bin/python
# -*- coding: utf-8 -*-

from twisted.application import internet, service
from twisted.protocols import basic
from twisted.internet import protocol, reactor, defer
import os

class Gatekeeper(object):
   """
   Responsible to route commands and stuff
   """

   knownCommands = 'setChannel play pause next prev setBackend status q exit quit bye'.split()

   def __init__(self, factory):
      self.__factory = factory

   def route( self, line ):
      command = line.split()[0]
      try:
         args = line.split()[1:]
      except IndexError:
         args = []

      if command == 'status':
         return "running"
      elif command in 'exit bye quit q'.split():
         self.__factory.doStop()
         return "bye"

class WJBProtocol(basic.LineReceiver):

   def connectionMade(self):
      self.transport.write("No rest for the wicked.\r\n") 

   def lineReceived( self, line ):
      print "<", line
      self.factory.processLine(line
            ).addErrback( lambda _: self.transport.write("Internal server error\r\n")
            ).addCallback( lambda m:
                      self.transport.write(m+"\r\n"))

   def disconnect(self):
      self.transport.loseConnection()

class WJBFactory( protocol.ServerFactory ):

   protocol = WJBProtocol
   gate     = None

   def __init__( self ):
      self.gate = Gatekeeper(self)

   def __repr__( self ): return "<WJBFactory>"

   def stopFactory(self):
      self.protocol.disconnect()

   def processLine( self, line ):
      if line.split()[0] not in self.gate.knownCommands:
         return defer.succeed( "ER: Unknown Command" )
      else:
         return defer.succeed( self.gate.route( line ) )

application = None
if os.getuid() == 0:
   print "WARNING: Process started as root. Trying to change to a less priviledged user..."
   try:
      application = service.Application('wickedjukebox', uid=1, gid=1)
   except:
      print "... failed to switch user."
      if config['core.allow_root_exec'] == 1:
         print "Running as superuser instead. THIS IS DANGEROUS! To disable this behaviour, set 'allow_root_exec' to 0 in config.ini"
         application = service.Application('wickedjukebox')
else:
   application = service.Application('wickedjukebox')

if application is not None:
   factory = WJBFactory()
   internet.TCPServer(61111, factory).setServiceParent(
       service.IServiceCollection(application))
else:
   print "Application failed to start up."

