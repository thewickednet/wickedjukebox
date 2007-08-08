# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xtest.ui'
#
# Created: Wed Aug  8 21:58:23 2007
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_wndXTest(object):
    def setupUi(self, wndXTest):
        wndXTest.setObjectName("wndXTest")
        wndXTest.resize(QtCore.QSize(QtCore.QRect(0,0,529,589).size()).expandedTo(wndXTest.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(wndXTest)
        self.centralwidget.setObjectName("centralwidget")

        self.vboxlayout = QtGui.QVBoxLayout(self.centralwidget)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")

        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.layoutWidget)
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.hboxlayout.addWidget(self.label)

        self.txtIP = QtGui.QLineEdit(self.layoutWidget)
        self.txtIP.setObjectName("txtIP")
        self.hboxlayout.addWidget(self.txtIP)

        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.hboxlayout.addWidget(self.label_2)

        self.txtPort = QtGui.QLineEdit(self.layoutWidget)
        self.txtPort.setObjectName("txtPort")
        self.hboxlayout.addWidget(self.txtPort)

        self.btnConnect = QtGui.QPushButton(self.layoutWidget)
        self.btnConnect.setObjectName("btnConnect")
        self.hboxlayout.addWidget(self.btnConnect)
        self.vboxlayout1.addLayout(self.hboxlayout)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.label_3 = QtGui.QLabel(self.layoutWidget)
        self.label_3.setObjectName("label_3")
        self.vboxlayout2.addWidget(self.label_3)

        self.lstMethods = QtGui.QListWidget(self.layoutWidget)
        self.lstMethods.setObjectName("lstMethods")
        self.vboxlayout2.addWidget(self.lstMethods)
        self.hboxlayout1.addLayout(self.vboxlayout2)

        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setMargin(0)
        self.vboxlayout3.setSpacing(6)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.label_4 = QtGui.QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")
        self.vboxlayout3.addWidget(self.label_4)

        self.txtParams = QtGui.QTextEdit(self.layoutWidget)
        self.txtParams.setObjectName("txtParams")
        self.vboxlayout3.addWidget(self.txtParams)
        self.hboxlayout1.addLayout(self.vboxlayout3)
        self.vboxlayout1.addLayout(self.hboxlayout1)

        self.btnExecute = QtGui.QPushButton(self.layoutWidget)
        self.btnExecute.setObjectName("btnExecute")
        self.vboxlayout1.addWidget(self.btnExecute)

        self.tabWidget = QtGui.QTabWidget(self.splitter)
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.vboxlayout4 = QtGui.QVBoxLayout(self.tab)
        self.vboxlayout4.setMargin(9)
        self.vboxlayout4.setSpacing(6)
        self.vboxlayout4.setObjectName("vboxlayout4")

        self.txtOutput = QtGui.QTextEdit(self.tab)

        font = QtGui.QFont(self.txtOutput.font())
        font.setFamily("Monospace")
        self.txtOutput.setFont(font)
        self.txtOutput.setReadOnly(True)
        self.txtOutput.setObjectName("txtOutput")
        self.vboxlayout4.addWidget(self.txtOutput)
        self.tabWidget.addTab(self.tab,"")

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.vboxlayout5 = QtGui.QVBoxLayout(self.tab_2)
        self.vboxlayout5.setMargin(9)
        self.vboxlayout5.setSpacing(6)
        self.vboxlayout5.setObjectName("vboxlayout5")

        self.txtPython = QtGui.QTextEdit(self.tab_2)

        font = QtGui.QFont(self.txtPython.font())
        font.setFamily("Monospace")
        self.txtPython.setFont(font)
        self.txtPython.setObjectName("txtPython")
        self.vboxlayout5.addWidget(self.txtPython)
        self.tabWidget.addTab(self.tab_2,"")

        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")

        self.vboxlayout6 = QtGui.QVBoxLayout(self.tab_3)
        self.vboxlayout6.setMargin(9)
        self.vboxlayout6.setSpacing(6)
        self.vboxlayout6.setObjectName("vboxlayout6")

        self.txtError = QtGui.QTextEdit(self.tab_3)

        font = QtGui.QFont(self.txtError.font())
        font.setFamily("Monospace")
        self.txtError.setFont(font)
        self.txtError.setObjectName("txtError")
        self.vboxlayout6.addWidget(self.txtError)
        self.tabWidget.addTab(self.tab_3,"")
        self.vboxlayout.addWidget(self.splitter)
        wndXTest.setCentralWidget(self.centralwidget)

        self.statusbar = QtGui.QStatusBar(wndXTest)
        self.statusbar.setObjectName("statusbar")
        wndXTest.setStatusBar(self.statusbar)

        self.retranslateUi(wndXTest)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(wndXTest)

    def retranslateUi(self, wndXTest):
        wndXTest.setWindowTitle(QtGui.QApplication.translate("wndXTest", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("wndXTest", "IP", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("wndXTest", "Port", None, QtGui.QApplication.UnicodeUTF8))
        self.btnConnect.setText(QtGui.QApplication.translate("wndXTest", "Connect", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("wndXTest", "Available functions", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("wndXTest", "Parameters (one param per line)", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExecute.setText(QtGui.QApplication.translate("wndXTest", "Execute", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("wndXTest", "JSON Output", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("wndXTest", "Python Representation", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("wndXTest", "Error", None, QtGui.QApplication.UnicodeUTF8))

