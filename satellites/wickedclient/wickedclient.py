import sys, os
from PyQt4 import QtCore, QtGui
from ui_mainwindow import Ui_MainWindow
import MySQLdb
import datetime

CON     = MySQLdb.connect( host="192.168.1.2", user="wjb", passwd="wjb", db="wjukebox" )
CUR     = CON.cursor()
CHANNEL = 2

class StartQT4(QtGui.QMainWindow):

   def __init__(self, parent=None):
      QtGui.QWidget.__init__(self, parent)
      self.ui = Ui_MainWindow()
      self.ui.setupUi(self)

      self.update_view()
      self.find()
      self.refresh_dpl()
      self.load_artists()
      self.timer = QtCore.QTimer()
      QtCore.QObject.connect(self.timer, QtCore.SIGNAL('timeout()'), self.update_view )
      self.timer.start(5000)


      QtCore.QObject.connect(self.ui.edtFind, QtCore.SIGNAL('returnPressed()'), self.find )
      QtCore.QObject.connect(self.ui.lbArtists, QtCore.SIGNAL('currentItemChanged(QListWidgetItem*, QListWidgetItem*)'), self.find_by_artist )
      QtCore.QObject.connect(self.ui.lbAlbums, QtCore.SIGNAL('currentItemChanged(QListWidgetItem*, QListWidgetItem*)'), self.find_by_album )
      QtCore.QObject.connect(self.ui.lbSongs, QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem*)'), self.enqueue )
      QtCore.QObject.connect(self.ui.btnQueue, QtCore.SIGNAL('clicked()'), self.enqueue )
      QtCore.QObject.connect(self.ui.btnSaveDPL, QtCore.SIGNAL('clicked()'), self.save_dpl )

   def update_view(self):
      self.ui.lbQueue.clear()
      self.ui.lbHistory.clear()
      sql = "SELECT channel, track, TIME_FORMAT(time, '%%H:%%i') FROM history WHERE channel=%s LIMIT 0,20"
      CUR.execute(sql, (CHANNEL))
      history = CUR.fetchall()
      first_item = None
      for song in history:
         item = QtGui.QListWidgetItem( "[%s] %s" % (song[2], song[1]) )
         if first_item is None:
            first_item = item
         self.ui.lbHistory.insertItem(0, item)
      self.ui.lbHistory.scrollToItem(first_item)

      self.ui.lbQueue.clear()
      sql = "SELECT a.name, s.title FROM queue q INNER JOIN song s ON (q.song_id = s.id) INNER JOIN artist a ON (s.artist_id = a.id) ORDER BY q.added"
      CUR.execute(sql)
      queue = CUR.fetchall()
      for song in queue:
         item = QtGui.QListWidgetItem( "%s - %s" % (song[0], song[1]) )
         self.ui.lbQueue.addItem(item)

      current_song_text = self.get_current_song()
      self.ui.lblSong.setText(current_song_text)

      #debug# test if this fixes the static history
      CON.commit()

   def find(self):
      text = str( self.ui.edtFind.text() )
      artists = self.find_artists(text)

      self.ui.lbArtists.clear()
      for a in artists:
         item = QtGui.QListWidgetItem( a[1] )
         item.setData( QtCore.Qt.UserRole, QtCore.QVariant(a[0]) )
         self.ui.lbArtists.addItem( item )

      self.ui.lbSongs.clear()
      if (text != ""):
         songs   = self.find_songs(text)
         for s in songs:
            item = QtGui.QListWidgetItem( "%s - %s - %s" % (s[1], s[2], s[3]) )
            item.setData( QtCore.Qt.UserRole, QtCore.QVariant(s[0]) )
            self.ui.lbSongs.addItem( item )

      self.ui.lbAlbums.clear()
      if (text != ""):
         albums   = self.find_albums(text)
         for a in albums:
            item = QtGui.QListWidgetItem( a[1] )
            item.setData( QtCore.Qt.UserRole, QtCore.QVariant(a[0]) )
            self.ui.lbAlbums.addItem( item )

   def find_by_album(self, item, previous):

      try:
         album = str(item.text())
      except:
         album = "unknown album"

      sql = """SELECT s.id, title, a.name
               FROM song s
                  INNER JOIN artist a ON (s.artist_id = a.id)
               WHERE s.album_id=%s
               ORDER BY s.track_no"""
      album_id = item.data(QtCore.Qt.UserRole).toInt()[0]
      CUR.execute(sql, (album_id))
      songs = CUR.fetchall()
      self.ui.lbSongs.clear()
      for s in songs:
         item = QtGui.QListWidgetItem( "%s - %s" % (s[2], s[1]) )
         item.setData( QtCore.Qt.UserRole, QtCore.QVariant(s[0]) )
         self.ui.lbSongs.addItem( item )

   def find_by_artist(self, item, previous):

      try:
         artist = str(item.text())
      except:
         artist = "unknown artist"

      artist_id = item.data(QtCore.Qt.UserRole).toInt()[0]

      # load all albums from this artist
      sql = """SELECT id, name
               FROM album
               WHERE artist_id=%s
               ORDER BY name"""
      CUR.execute(sql, (artist_id))
      albums = CUR.fetchall()
      self.ui.lbAlbums.clear()
      for a in albums:
         item = QtGui.QListWidgetItem( "%s" % (a[1]) )
         item.setData( QtCore.Qt.UserRole, QtCore.QVariant(a[0]) )
         self.ui.lbAlbums.addItem( item )

      # load all songs from this artist
      sql = """SELECT s.id, title, b.name
               FROM song s
                  INNER JOIN album b ON (s.album_id = b.id)
               WHERE s.artist_id=%s
               ORDER BY b.name, s.track_no"""
      CUR.execute(sql, (artist_id))
      songs = CUR.fetchall()
      self.ui.lbSongs.clear()
      for s in songs:
         item = QtGui.QListWidgetItem( "%s - %s" % (s[2], s[1]) )
         item.setData( QtCore.Qt.UserRole, QtCore.QVariant(s[0]) )
         self.ui.lbSongs.addItem( item )

   def find_albums(self, name):
      sql = "SELECT id, name FROM album WHERE name LIKE %s ORDER BY name"
      CUR.execute( sql, ("%%%s%%" % name) )
      return CUR.fetchall()

   def find_artists(self, name):
      sql = "SELECT id, name FROM artist WHERE name LIKE %s ORDER BY name"
      CUR.execute( sql, ("%%%s%%" % name) )
      return CUR.fetchall()

   def find_songs(self, name):
      sql = """SELECT s.id, a.name, title, b.name
               FROM song s
                  INNER JOIN artist a ON (s.artist_id = a.id)
                  INNER JOIN album b ON (s.album_id = b.id)
               WHERE s.title LIKE %s
                  OR b.name LIKE %s
               ORDER BY a.name, b.name, s.track_no"""
      CUR.execute( sql, ("%%%s%%" % name, "%%%s%%" % name) )
      return CUR.fetchall()

   def enqueue(self, item=None):
      if item is None:
         item = self.ui.lbSongs.currentItem()
      song_id = item.data(QtCore.Qt.UserRole).toInt()[0]
      sql = "INSERT INTO queue ( song_id, channel_id, added ) VALUES (%s, %s, NOW())"
      CUR.execute( sql, (song_id, CHANNEL) )
      CON.commit()
      self.update_view()

   def refresh_dpl(self):
      sql = "SELECT id, query, group_id FROM dynamicPlaylist WHERE label='wickedClient'"
      CUR.execute( sql )
      res = CUR.fetchone()
      if res[1] is not None:
         self.ui.edtDPL.setText( res[1] )
         if int(res[2]) != 0:
            self.ui.cbEnabled.setCheckState( QtCore.Qt.Checked )
         else:
            self.ui.cbEnabled.setCheckState( QtCore.Qt.Unchecked )

   def save_dpl(self):
      sql = "UPDATE dynamicPlaylist SET query=%s, group_id=%s WHERE label='wickedClient'"
      if self.ui.cbEnabled.checkState() == QtCore.Qt.Checked:
         enabled = 1
      else:
         enabled = 0
      CUR.execute( sql, (str(self.ui.edtDPL.toPlainText()), enabled) )
      CON.commit()

   def load_artists(self):
      self.ui.lbArtistsDPL.clear()
      for a in self.find_artists(""):
         item = QtGui.QListWidgetItem( a[1] )
         item.setData( QtCore.Qt.UserRole, QtCore.QVariant(a[0]) )
         self.ui.lbArtistsDPL.addItem( item )

   def get_current_song(self):
      sql = "SELECT a.name, s.title, CAST(value as UNSIGNED) FROM state st INNER JOIN song s ON (CAST(value as UNSIGNED) = s.id) INNER JOIN artist a ON (s.artist_id = a.id) WHERE state='current_song'"
      CUR.execute( sql )
      res = CUR.fetchone()
      return "%s - %s" % (res[0], res[1])

if __name__ == "__main__":

   app = QtGui.QApplication(sys.argv)

   dw = app.desktop().width()
   dh = app.desktop().height()

   myapp = StartQT4()
   myapp.setGeometry(
         int((dw - (dw - (dw / 2)) * 1.5) / 2),
         int((dh - (dh - (dh / 2)) * 1.5) / 2),
         int((dw - (dw / 2)) * 1.5),
         int((dh - (dh / 2)) * 1.5))
   myapp.show()
   sys.exit(app.exec_())
