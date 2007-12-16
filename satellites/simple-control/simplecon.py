import sys, pickle, os
from PyQt4 import QtCore, QtGui
from ui_simplecontrol import Ui_wndSimpleController
import xmlrpclib
from settings import xmlrpc_host, xmlrpc_port, channel_id
import simplejson


class StartQT4(QtGui.QMainWindow):

   def __init__(self, parent=None):
      self.server = xmlrpclib.Server('http://%s:%d' % (xmlrpc_host, xmlrpc_port))
      QtGui.QWidget.__init__(self, parent)
      self.ui = Ui_wndSimpleController()
      self.ui.setupUi(self)

      if QtGui.QSystemTrayIcon.isSystemTrayAvailable():
         # set up system tray icon
         self.tray_icon = QtGui.QSystemTrayIcon()
         self.tray_icon.setIcon( QtGui.QIcon(":/icons/icons/player_play.png") )
         self.tray_icon.show()
         QtCore.QObject.connect(self.tray_icon, QtCore.SIGNAL('activated(QSystemTrayIcon::ActivationReason)'), self.tray_clicked)


      self.timer = QtCore.QTimer()
      QtCore.QObject.connect(self.timer, QtCore.SIGNAL('timeout()'), self.update_status )
      self.old_song_status = None
      self.timer.start(2000)

      QtCore.QObject.connect(self.ui.actionSkip, QtCore.SIGNAL('activated()'), self.skip )
      QtCore.QObject.connect(self.ui.actionStop, QtCore.SIGNAL('activated()'), self.stop )
      QtCore.QObject.connect(self.ui.actionPlay, QtCore.SIGNAL('activated()'), self.play )
      QtCore.QObject.connect(self.ui.actionPause, QtCore.SIGNAL('activated()'), self.pause )

   def update_status(self):
      print "updating status"
      data = self.server.getSongData(channel_id, -1)
      if type(data) == type(""):
         data = simplejson.loads(data)
         if data is not None:
            display_string = "%(artist)s - %(title)s - %(album)s" % (data)
            if self.old_song_status != data:
               self.tray_icon.showMessage("Currently playing", display_string)
               self.old_song_status = data
               self.ui.statusBar.showMessage(display_string)
      else:
         self.ui.statusBar.showMessage("error")

   def tray_clicked(self, reason):
      if reason == QtGui.QSystemTrayIcon.Trigger:
         if self.isVisible():
            self.hide()
         else:
            self.show()
      else:
         pass

   def stop(self):
      try:
         self.server.stop(channel_id)
      except xmlrpclib.Fault:
         QtGui.QMessageBox.warning(
               None,
               'XMLRPC-Fault',
               'Fault object received when executing "stop"\n' +
                  'Did you specify the correct channel_id in settings.py?',
               QtGui.QMessageBox.Ok
               )

   def play(self):
      try:
         print self.server.play(channel_id)
      except xmlrpclib.Fault:
         QtGui.QMessageBox.warning(
               None,
               'XMLRPC-Fault',
               'Fault object received when executing "stop"\n' +
                  'Did you specify the correct channel_id in settings.py?',
               QtGui.QMessageBox.Ok
               )

   def pause(self):
      try:
         print self.server.pause(channel_id)
      except xmlrpclib.Fault:
         QtGui.QMessageBox.warning(
               None,
               'XMLRPC-Fault',
               'Fault object received when executing "pause"\n' +
                  'Did you specify the correct channel_id in settings.py?',
               QtGui.QMessageBox.Ok
               )

   def skip(self):
      try:
         print self.server.next(channel_id)
      except xmlrpclib.Fault:
         QtGui.QMessageBox.warning(
               None,
               'XMLRPC-Fault',
               'Fault object received when executing "skip"\n' +
                  'Did you specify the correct channel_id in settings.py?',
               QtGui.QMessageBox.Ok
               )

if __name__ == "__main__":

   app = QtGui.QApplication(sys.argv)
   myapp = StartQT4()
   myapp.show()
   sys.exit(app.exec_())


