import sys
from PyQt4 import QtCore, QtGui
from ui.ui_genrebrowser import Ui_MainWindow
from demon.model import *

class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        self.__sess = create_session()
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.updateGenres()
        QtCore.QObject.connect(self.ui.lstGenre, QtCore.SIGNAL('currentItemChanged(QListWidgetItem*, QListWidgetItem*)'), self.updateSongs)

    def __del__(self):
       self.__sess.close()

    def updateGenres(self):
        genres = self.__sess.query( Genre ).select( order_by=[Genre.c.name])
        for i,genre in enumerate(genres):
           li = QtGui.QListWidgetItem("%s (%d)" % (genre.name, len(genre.songs)), self.ui.lstGenre)
           li.dbObj = genre

    def updateSongs(self, currentItem, oldItem=None):

       self.ui.tblSongs.clearContents()
       for i,song in enumerate(currentItem.dbObj.songs):
          self.ui.tblSongs.setRowCount(i+1)
          tiArtist = QtGui.QTableWidgetItem( song.artist.name )
          tiAlbum  = QtGui.QTableWidgetItem( song.album.name )
          tiSong   = QtGui.QTableWidgetItem( song.title )
          tiPath   = QtGui.QTableWidgetItem( song.localpath )
          self.ui.tblSongs.setItem(i,0,tiArtist)
          self.ui.tblSongs.setItem(i,1,tiAlbum)
          self.ui.tblSongs.setItem(i,2,tiSong)
          self.ui.tblSongs.setItem(i,3,tiPath)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())


