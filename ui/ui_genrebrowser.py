# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GenreBrowser.ui'
#
# Created: Sat Jun 30 14:04:51 2007
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,800,600).size()).expandedTo(MainWindow.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.vboxlayout = QtGui.QVBoxLayout(self.centralwidget)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName("widget")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.widget)
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName("label")
        self.vboxlayout1.addWidget(self.label)

        self.lstGenre = QtGui.QListWidget(self.widget)
        self.lstGenre.setObjectName("lstGenre")
        self.vboxlayout1.addWidget(self.lstGenre)

        self.widget1 = QtGui.QWidget(self.splitter)
        self.widget1.setObjectName("widget1")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.widget1)
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.label_2 = QtGui.QLabel(self.widget1)
        self.label_2.setObjectName("label_2")
        self.vboxlayout2.addWidget(self.label_2)

        self.tblSongs = QtGui.QTableWidget(self.widget1)
        self.tblSongs.setObjectName("tblSongs")
        self.vboxlayout2.addWidget(self.tblSongs)
        self.vboxlayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,800,32))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Genre", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Songs", None, QtGui.QApplication.UnicodeUTF8))
        self.tblSongs.clear()
        self.tblSongs.setColumnCount(4)
        self.tblSongs.setRowCount(0)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("MainWindow", "Artist", None, QtGui.QApplication.UnicodeUTF8))
        self.tblSongs.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("MainWindow", "Album", None, QtGui.QApplication.UnicodeUTF8))
        self.tblSongs.setHorizontalHeaderItem(1,headerItem1)

        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(QtGui.QApplication.translate("MainWindow", "Song", None, QtGui.QApplication.UnicodeUTF8))
        self.tblSongs.setHorizontalHeaderItem(2,headerItem2)

        headerItem3 = QtGui.QTableWidgetItem()
        headerItem3.setText(QtGui.QApplication.translate("MainWindow", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.tblSongs.setHorizontalHeaderItem(3,headerItem3)

