import sys, pickle, os
from PyQt4 import QtCore, QtGui
from ui_simplecontrol import Ui_wndSimpleController
import xmlrpclib

class StartQT4(QtGui.QMainWindow):

   def __init__(self, parent=None):
      self.server = xmlrpclib.Server('http://192.168.1.2:61112')
      QtGui.QWidget.__init__(self, parent)
      self.ui = Ui_wndSimpleController()
      self.ui.setupUi(self)

      QtCore.QObject.connect(self.ui.actionSkip, QtCore.SIGNAL('activated()'), self.skip )
      QtCore.QObject.connect(self.ui.actionStop, QtCore.SIGNAL('activated()'), self.stop )
      QtCore.QObject.connect(self.ui.actionPlay, QtCore.SIGNAL('activated()'), self.play )

   def stop(self):
      print self.server.stop()

   def play(self):
      print self.server.play()

   def skip(self):
      print self.server.next()

if __name__ == "__main__":

   app = QtGui.QApplication(sys.argv)
   myapp = StartQT4()
   myapp.show()
   sys.exit(app.exec_())


