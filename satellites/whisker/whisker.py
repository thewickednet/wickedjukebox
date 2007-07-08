import sys, pickle, os
from PyQt4 import QtCore, QtGui
from ui_whisker import Ui_wndWhisker
import xmlrpclib
from datetime import datetime
from time import strptime

try:
   import simplejson
   jsonEnabled = False
except:
   jsonEnabled = False

def unmarshal( data ):
   if jsonEnabled:
      return simplejson.loads( data )
   else:
      return data

class StartQT4(QtGui.QMainWindow):

   _data  = []
   _persistence_delta = 10.0 * 86400 # 10 days
   _delta_steps       = 5

   def __init__(self, parent=None):
      QtGui.QWidget.__init__(self, parent)
      self.ui = Ui_wndWhisker()
      self.ui.setupUi(self)
      QtCore.QObject.connect(self.ui.actionAdd_Item, QtCore.SIGNAL('activated()'), self.showAddItem )
      QtCore.QObject.connect(self.ui.actionUpdate, QtCore.SIGNAL('activated()'), self.updateList )
      QtCore.QObject.connect(self.ui.actionSave, QtCore.SIGNAL('activated()'), self.save )
      QtCore.QObject.connect(self.ui.actionPull, QtCore.SIGNAL('activated()'), self.pullSong )
      try:
         self._data = pickle.load( open('data.pkl', 'rb') )
         self.initList()
      except:
         pass
      self.ui.actionSave.setEnabled( False )
      self.ping()

   def pullSong(self):
      try:
         from ui_add_item import Ui_Dialog
         server = xmlrpclib.Server('http://192.168.1.2:61112')
         songid = unmarshal( server.getCurrentSong() )
         songdata = unmarshal (server.getSongData( songid ) )
         print songdata
         dlg = QtGui.QDialog()
         ui  = Ui_Dialog()
         ui.setupUi( dlg )
         ui.txtArtist.setText( songdata['artist'] )
         ui.txtAlbum.setText( songdata['album'] )
         ui.txtSong.setText( songdata['title'] )
         if dlg.exec_():
            artist = ui.txtArtist.text()
            album  = ui.txtAlbum.text()
            song   = ui.txtSong.text()
            rocks  = (ui.cbRocks.checkState() == 2) or False
            self._data.append({
               'artist':    '%s' % artist,
               'album':     '%s' % album,
               'song':      '%s' % song,
               'rocks':     rocks,
               'available': None,
               'date':      datetime.now(),
               'weight':    1,
               })
            self.addSong(self._data[-1])
      except:
         pass

   def ping(self):
      try:
         server = xmlrpclib.Server('http://192.168.1.2:61112')
         alive  = unmarshal( server.ping() )
         if alive is True:
            self.ui.actionPull.setEnabled( True )
         else:
            self.ui.actionPull.setEnabled( True )
      except:
         self.ui.actionPull.setEnabled( False )


   def calcWeight(self, age):

      # TODO: Hardcoded to 1. The rest below it not yet doing what I want.
      return 1

      if self._persistence_delta - age < 0:
         return 0
      else:
         import math
         coeff = 1-(age/self._persistence_delta)
         return 1-(1.0/(math.log(coeff**0.5+1.5))-1)

   def save(self):
      pickle.dump( self._data, open('data.pkl', 'w'), -1 )
      self.ui.actionSave.setEnabled( False )

   def initList(self):
      for song in self._data:
         self.addSong(song)

   def showAddItem(self):
      from ui_add_item import Ui_Dialog
      dlg = QtGui.QDialog()
      ui  = Ui_Dialog()
      ui.setupUi( dlg )
      if dlg.exec_():
         artist = ui.txtArtist.text()
         album  = ui.txtAlbum.text()
         song   = ui.txtSong.text()
         self._data.append({
            'artist':    '%s' % artist,
            'album':     '%s' % album,
            'song':      '%s' % song,
            'rocks':     True,
            'available': None,
            'date':      datetime.now(),
            'weight':    1,
            })
         self.addSong(self._data[-1])

   def addSong(self, data):
      t = QtGui.QTreeWidgetItem(self.ui.triFavourites);
      t.setText(0, data['artist']);
      t.setText(1, data['album']);
      t.setText(2, data['song']);
      t.setText(3, '%s' % data['rocks']);
      t.setText(4, '%s' % data['available']);
      t.setText(5, '%s' % data['date']);
      t.setText(6, '%s' % data['weight']);
      self.ui.actionSave.setEnabled( True )

   def updateList(self):
      r = self.ui.triFavourites.findItems('', QtCore.Qt.MatchContains)
      now = datetime.now()
      for i,item in enumerate(self._data):
         treeItem = self.ui.triFavourites.topLevelItem(i)
         delta = now - item['date']
         treeItem.setText( 6, '%3.4f' % self.calcWeight(delta.seconds) )


if __name__ == "__main__":
   #server = xmlrpclib.Server('http://192.168.1.2:61113')
   #albums = unmarshal( server.get_albums("Wir sind Helden") )
   #for a in albums:
   #   songs = unmarshal( server.get_album_songs( a[0] ) )
   #   print "%010d | %30s | %d" % (a[0], a[1], len(songs))
   #   for s in songs:
   #      print s

   app = QtGui.QApplication(sys.argv)
   myapp = StartQT4()
   myapp.show()
   sys.exit(app.exec_())


