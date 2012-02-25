# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simpleControl.ui'
#
# Created: Sun Dec 16 13:31:02 2007
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_wndSimpleController(object):
    def setupUi(self, wndSimpleController):
        wndSimpleController.setObjectName("wndSimpleController")
        wndSimpleController.resize(QtCore.QSize(QtCore.QRect(0,0,258,82).size()).expandedTo(wndSimpleController.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(wndSimpleController)
        self.centralwidget.setObjectName("centralwidget")

        self.hboxlayout = QtGui.QHBoxLayout(self.centralwidget)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(9)
        self.hboxlayout.setObjectName("hboxlayout")
        wndSimpleController.setCentralWidget(self.centralwidget)

        self.toolBar = QtGui.QToolBar(wndSimpleController)
        self.toolBar.setOrientation(QtCore.Qt.Horizontal)
        self.toolBar.setObjectName("toolBar")
        wndSimpleController.addToolBar(self.toolBar)

        self.statusBar = QtGui.QStatusBar(wndSimpleController)
        self.statusBar.setObjectName("statusBar")
        wndSimpleController.setStatusBar(self.statusBar)

        self.actionSkip = QtGui.QAction(wndSimpleController)
        self.actionSkip.setIcon(QtGui.QIcon(":/icons/icons/player_fwd.png"))
        self.actionSkip.setObjectName("actionSkip")

        self.actionPlay = QtGui.QAction(wndSimpleController)
        self.actionPlay.setIcon(QtGui.QIcon(":/icons/icons/player_play.png"))
        self.actionPlay.setObjectName("actionPlay")

        self.actionStop = QtGui.QAction(wndSimpleController)
        self.actionStop.setIcon(QtGui.QIcon(":/icons/icons/player_stop.png"))
        self.actionStop.setObjectName("actionStop")

        self.actionPause = QtGui.QAction(wndSimpleController)
        self.actionPause.setIcon(QtGui.QIcon(":/icons/icons/player_pause.png"))
        self.actionPause.setObjectName("actionPause")
        self.toolBar.addAction(self.actionStop)
        self.toolBar.addAction(self.actionPause)
        self.toolBar.addAction(self.actionPlay)
        self.toolBar.addAction(self.actionSkip)

        self.retranslateUi(wndSimpleController)
        QtCore.QMetaObject.connectSlotsByName(wndSimpleController)

    def retranslateUi(self, wndSimpleController):
        wndSimpleController.setWindowTitle(QtGui.QApplication.translate("wndSimpleController", "Simple Controller", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSkip.setText(QtGui.QApplication.translate("wndSimpleController", "skip", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPlay.setText(QtGui.QApplication.translate("wndSimpleController", "play", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStop.setText(QtGui.QApplication.translate("wndSimpleController", "stop", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPause.setText(QtGui.QApplication.translate("wndSimpleController", "pause", None, QtGui.QApplication.UnicodeUTF8))

import rc_icons_rc
