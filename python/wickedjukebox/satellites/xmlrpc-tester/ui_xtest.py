# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xtest.ui'
#
# Created: Wed Aug 15 14:44:42 2007
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_wndXTest(object):
    def setupUi(self, wndXTest):
        wndXTest.setObjectName("wndXTest")
        wndXTest.resize(QtCore.QSize(QtCore.QRect(0,0,584,670).size()).expandedTo(wndXTest.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(wndXTest)
        self.centralwidget.setObjectName("centralwidget")

        self.vboxlayout = QtGui.QVBoxLayout(self.centralwidget)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.hboxlayout.addWidget(self.label)

        self.txtIP = QtGui.QLineEdit(self.centralwidget)
        self.txtIP.setObjectName("txtIP")
        self.hboxlayout.addWidget(self.txtIP)

        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.hboxlayout.addWidget(self.label_2)

        self.txtPort = QtGui.QLineEdit(self.centralwidget)
        self.txtPort.setObjectName("txtPort")
        self.hboxlayout.addWidget(self.txtPort)

        self.btnConnect = QtGui.QPushButton(self.centralwidget)
        self.btnConnect.setObjectName("btnConnect")
        self.hboxlayout.addWidget(self.btnConnect)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.splitter_2 = QtGui.QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")

        self.widget = QtGui.QWidget(self.splitter_2)
        self.widget.setObjectName("widget")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.widget)
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.vboxlayout1.addWidget(self.label_3)

        self.lstMethods = QtGui.QListWidget(self.widget)
        self.lstMethods.setBaseSize(QtCore.QSize(200,0))
        self.lstMethods.setObjectName("lstMethods")
        self.vboxlayout1.addWidget(self.lstMethods)

        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setMinimumSize(QtCore.QSize(320,16))
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")

        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.layoutWidget)
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.label_5 = QtGui.QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")
        self.vboxlayout2.addWidget(self.label_5)

        self.txtDocstring = QtGui.QTextEdit(self.layoutWidget)
        self.txtDocstring.setMinimumSize(QtCore.QSize(0,150))
        self.txtDocstring.setReadOnly(True)
        self.txtDocstring.setAcceptRichText(True)
        self.txtDocstring.setObjectName("txtDocstring")
        self.vboxlayout2.addWidget(self.txtDocstring)

        self.layoutWidget1 = QtGui.QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.layoutWidget1)
        self.vboxlayout3.setMargin(0)
        self.vboxlayout3.setSpacing(6)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.label_4 = QtGui.QLabel(self.layoutWidget1)
        self.label_4.setObjectName("label_4")
        self.vboxlayout3.addWidget(self.label_4)

        self.txtParams = QtGui.QTextEdit(self.layoutWidget1)
        self.txtParams.setTabChangesFocus(True)
        self.txtParams.setObjectName("txtParams")
        self.vboxlayout3.addWidget(self.txtParams)
        self.vboxlayout.addWidget(self.splitter_2)

        self.btnExecute = QtGui.QPushButton(self.centralwidget)
        self.btnExecute.setObjectName("btnExecute")
        self.vboxlayout.addWidget(self.btnExecute)

        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
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
        self.txtOutput.setTabChangesFocus(True)
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
        self.txtPython.setReadOnly(True)
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
        self.txtError.setReadOnly(True)
        self.txtError.setObjectName("txtError")
        self.vboxlayout6.addWidget(self.txtError)
        self.tabWidget.addTab(self.tab_3,"")
        self.vboxlayout.addWidget(self.tabWidget)
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
        self.label_5.setText(QtGui.QApplication.translate("wndXTest", "Method docstring", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("wndXTest", "Parameters (one param per line)", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExecute.setText(QtGui.QApplication.translate("wndXTest", "Execute", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("wndXTest", "JSON Output", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("wndXTest", "Python Representation", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("wndXTest", "Error", None, QtGui.QApplication.UnicodeUTF8))

