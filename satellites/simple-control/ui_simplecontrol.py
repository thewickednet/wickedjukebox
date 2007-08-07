# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simpleControl.ui'
#
# Created: Tue Aug  7 20:17:01 2007
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_wndSimpleController(object):
    def setupUi(self, wndSimpleController):
        wndSimpleController.setObjectName("wndSimpleController")
        wndSimpleController.resize(QtCore.QSize(QtCore.QRect(0,0,135,57).size()).expandedTo(wndSimpleController.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(wndSimpleController)
        self.centralwidget.setObjectName("centralwidget")

        self.hboxlayout = QtGui.QHBoxLayout(self.centralwidget)
        self.hboxlayout.setMargin(9)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")
        wndSimpleController.setCentralWidget(self.centralwidget)

        self.toolBar = QtGui.QToolBar(wndSimpleController)
        self.toolBar.setOrientation(QtCore.Qt.Horizontal)
        self.toolBar.setObjectName("toolBar")
        wndSimpleController.addToolBar(self.toolBar)

        self.actionSkip = QtGui.QAction(wndSimpleController)
        self.actionSkip.setIcon(QtGui.QIcon("icons/player_fwd.png"))
        self.actionSkip.setObjectName("actionSkip")

        self.actionPlay = QtGui.QAction(wndSimpleController)
        self.actionPlay.setIcon(QtGui.QIcon("icons/player_play.png"))
        self.actionPlay.setObjectName("actionPlay")

        self.actionStop = QtGui.QAction(wndSimpleController)
        self.actionStop.setIcon(QtGui.QIcon("icons/player_stop.png"))
        self.actionStop.setObjectName("actionStop")
        self.toolBar.addAction(self.actionStop)
        self.toolBar.addAction(self.actionPlay)
        self.toolBar.addAction(self.actionSkip)

        self.retranslateUi(wndSimpleController)
        QtCore.QMetaObject.connectSlotsByName(wndSimpleController)

    def retranslateUi(self, wndSimpleController):
        wndSimpleController.setWindowTitle(QtGui.QApplication.translate("wndSimpleController", "Simple Controller", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSkip.setText(QtGui.QApplication.translate("wndSimpleController", "skip", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPlay.setText(QtGui.QApplication.translate("wndSimpleController", "play", None, QtGui.QApplication.UnicodeUTF8))
        self.actionStop.setText(QtGui.QApplication.translate("wndSimpleController", "stop", None, QtGui.QApplication.UnicodeUTF8))

