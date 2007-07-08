# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Whisker.ui'
#
# Created: Sun Jul  8 13:30:54 2007
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_wndWhisker(object):
    def setupUi(self, wndWhisker):
        wndWhisker.setObjectName("wndWhisker")
        wndWhisker.resize(QtCore.QSize(QtCore.QRect(0,0,785,362).size()).expandedTo(wndWhisker.minimumSizeHint()))
        wndWhisker.setAcceptDrops(False)

        self.centralwidget = QtGui.QWidget(wndWhisker)
        self.centralwidget.setObjectName("centralwidget")

        self.vboxlayout = QtGui.QVBoxLayout(self.centralwidget)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.triFavourites = QtGui.QTreeWidget(self.centralwidget)
        self.triFavourites.setObjectName("triFavourites")
        self.vboxlayout.addWidget(self.triFavourites)
        wndWhisker.setCentralWidget(self.centralwidget)

        self.toolBar = QtGui.QToolBar(wndWhisker)
        self.toolBar.setOrientation(QtCore.Qt.Horizontal)
        self.toolBar.setObjectName("toolBar")
        wndWhisker.addToolBar(self.toolBar)

        self.actionAdd_Item = QtGui.QAction(wndWhisker)
        self.actionAdd_Item.setIcon(QtGui.QIcon("icons/add.png"))
        self.actionAdd_Item.setObjectName("actionAdd_Item")

        self.actionExit = QtGui.QAction(wndWhisker)
        self.actionExit.setIcon(QtGui.QIcon("icons/exit.png"))
        self.actionExit.setObjectName("actionExit")

        self.actionUpdate = QtGui.QAction(wndWhisker)
        self.actionUpdate.setIcon(QtGui.QIcon("icons/reload.png"))
        self.actionUpdate.setObjectName("actionUpdate")

        self.actionSave = QtGui.QAction(wndWhisker)
        self.actionSave.setIcon(QtGui.QIcon("icons/save_all.png"))
        self.actionSave.setObjectName("actionSave")

        self.actionPull = QtGui.QAction(wndWhisker)
        self.actionPull.setIcon(QtGui.QIcon("icons/wizard.png"))
        self.actionPull.setObjectName("actionPull")
        self.toolBar.addAction(self.actionAdd_Item)
        self.toolBar.addAction(self.actionPull)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionUpdate)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionExit)

        self.retranslateUi(wndWhisker)
        QtCore.QObject.connect(self.actionExit,QtCore.SIGNAL("activated()"),wndWhisker.close)
        QtCore.QMetaObject.connectSlotsByName(wndWhisker)

    def retranslateUi(self, wndWhisker):
        wndWhisker.setWindowTitle(QtGui.QApplication.translate("wndWhisker", "Whisker", None, QtGui.QApplication.UnicodeUTF8))
        self.triFavourites.headerItem().setText(0,QtGui.QApplication.translate("wndWhisker", "Artist", None, QtGui.QApplication.UnicodeUTF8))
        self.triFavourites.headerItem().setText(1,QtGui.QApplication.translate("wndWhisker", "Album", None, QtGui.QApplication.UnicodeUTF8))
        self.triFavourites.headerItem().setText(2,QtGui.QApplication.translate("wndWhisker", "Song", None, QtGui.QApplication.UnicodeUTF8))
        self.triFavourites.headerItem().setText(3,QtGui.QApplication.translate("wndWhisker", "I like it", None, QtGui.QApplication.UnicodeUTF8))
        self.triFavourites.headerItem().setText(4,QtGui.QApplication.translate("wndWhisker", "Available on server", None, QtGui.QApplication.UnicodeUTF8))
        self.triFavourites.headerItem().setText(5,QtGui.QApplication.translate("wndWhisker", "Date Added", None, QtGui.QApplication.UnicodeUTF8))
        self.triFavourites.headerItem().setText(6,QtGui.QApplication.translate("wndWhisker", "Score Weight", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdd_Item.setText(QtGui.QApplication.translate("wndWhisker", "Add Item", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setText(QtGui.QApplication.translate("wndWhisker", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUpdate.setText(QtGui.QApplication.translate("wndWhisker", "Update", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("wndWhisker", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPull.setText(QtGui.QApplication.translate("wndWhisker", "Pull from Jukebox", None, QtGui.QApplication.UnicodeUTF8))

