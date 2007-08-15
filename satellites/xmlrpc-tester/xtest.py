import sys
from PyQt4 import QtCore, QtGui
from ui_xtest import Ui_wndXTest
import xmlrpclib
import simplejson
import pprint

default_ip   = "192.168.1.2"
default_port = "65222"
autoconnect  = True

def unmarshal( data ):
   return simplejson.loads( data )

class StartQT4(QtGui.QMainWindow):

   def __init__(self, parent=None):
      QtGui.QWidget.__init__(self, parent)
      self.ui = Ui_wndXTest()
      self.ui.setupUi(self)
      QtCore.QObject.connect(self.ui.btnConnect, QtCore.SIGNAL('clicked()'), self.connect )
      QtCore.QObject.connect(self.ui.btnExecute, QtCore.SIGNAL('clicked()'), self.execute )
      QtCore.QObject.connect(self.ui.lstMethods, QtCore.SIGNAL('itemSelectionChanged()'), self.methodHelp )
      self.__server = None
      self.ui.txtIP.setText(default_ip)
      self.ui.txtPort.setText(default_port)
      self.updateFuncList()
      self.enableCalls(False)

      if autoconnect:
         self.connect()

   def enableCalls(self, state):
      self.ui.lstMethods.setEnabled(state)
      self.ui.txtParams.setEnabled(state)
      self.ui.btnExecute.setEnabled(state)

   def connect(self):
      ip     = self.ui.txtIP.text()
      port   = self.ui.txtPort.text()
      self.ui.statusbar.showMessage("connecting to http://%s:%s" % (ip, port) )
      try:
         self.__server = xmlrpclib.Server('http://%s:%s' % (ip, port))
         self.ui.statusbar.showMessage("connected to http://%s:%s" % (ip, port) )
         self.enableCalls(True)
      except Exception, ex:
         QtGui.QMessageBox.critical(self, "Error", "Unable to connect to http://%s:%s" % (ip, port))
         self.ui.statusbar.showMessage("Error connecting to http://%s:%s" % (ip, port), 6000 )
         print ex
         self.enableCalls(False)

   def methodHelp(self):
      funcname = self.ui.lstMethods.selectedItems()[0].text()
      docstring = self.__server.system.methodHelp(str(funcname))
      self.ui.txtDocstring.setText( docstring )

   def updateFuncList(self):
      funcs = [ x[5:] for x in dir(self) if x.startswith('call_') ]
      for f in funcs:
         QtGui.QListWidgetItem(f, self.ui.lstMethods)

   #def call_lsm(self, args):
   #   return self.__server.system.listMethods()

   def call_help(self, args):
      return self.__server.help()

   def call_next(self, args):
      return self.__server.next(int(args[0]))

   def call_enqueue(self, args):
      return self.__server.enqueue( int(args[0]),
                                    int(args[1]),
                                    int(args[2])
                                    )

   def call_enqueue_album(self, args):
      return self.__server.enqueue_album( int(args[0]) )

   def call_get_album_songs(self, args):
      return self.__server.get_album_songs( int(args[0]) )

   def call_get_albums(self, args):
      return self.__server.get_albums( int(args[0]) )

   def call_getCurrentSong(self, args):
      return self.__server.getCurrentSong( int(args[0]) )

   def call_getSongData(self, args):
      return self.__server.getSongData( int(args[0]) )

   def call_movebottom(self, args):
      return self.__server.movebottom( int(args[0]) )

   def call_movetop(self, args):
      return self.__server.movetop( int(args[0]) )

   def call_movedown(self, args):
      return self.__server.movedown( int(args[0]),
                                     int(args[1]),
                                     int(args[2]) )

   def call_moveup(self, args):
      return self.__server.moveup( int(args[0]),
                                   int(args[1]),
                                   int(args[2]) )

   def call_pause(self, args):
      return self.__server.pause( int(args[0]) )

   def call_ping(self, args):
      return self.__server.ping()

   def call_play(self, args):
      return self.__server.play( int(args[0]) )

   def call_queue_delete(self, args):
      return self.__server.queue_delete( int(args[0]) )

   def call_stop(self, args):
      return self.__server.stop( int(args[0]) )

   def call_current_queue(self, args):
      return self.__server.current_queue( int(args[0]) )

   def execute(self):
      func = self.ui.lstMethods.selectedItems()[0].text()
      para = str(self.ui.txtParams.toPlainText()).split()

      print "function:", func
      print "params:", para

      try:
         call = self.__getattribute__( "call_%s" % func )
         output = call(para)
         self.ui.txtError.setText( "" )
         self.ui.txtOutput.setText( str(output) )
         if output is not None:
            self.ui.txtPython.setText( pprint.pformat(unmarshal(output)) )
         self.ui.tabWidget.setCurrentIndex(1)
      except Exception, ex:
         self.ui.txtError.setText( "%s" % ex )
         self.ui.tabWidget.setCurrentIndex(2)

if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   myapp = StartQT4()
   myapp.show()
   sys.exit(app.exec_())


