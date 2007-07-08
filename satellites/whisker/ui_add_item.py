# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Whisker_addItem.ui'
#
# Created: Sun Jul  8 15:12:27 2007
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,440,189).size()).expandedTo(Dialog.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(Dialog)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.txtSong = QtGui.QLineEdit(Dialog)
        self.txtSong.setObjectName("txtSong")
        self.gridlayout.addWidget(self.txtSong,2,1,1,2)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem,3,0,1,2)

        self.txtAlbum = QtGui.QLineEdit(Dialog)
        self.txtAlbum.setObjectName("txtAlbum")
        self.gridlayout.addWidget(self.txtAlbum,1,1,1,2)

        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)

        self.txtArtist = QtGui.QLineEdit(Dialog)
        self.txtArtist.setObjectName("txtArtist")
        self.gridlayout.addWidget(self.txtArtist,0,1,1,2)

        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,1,0,1,1)

        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridlayout.addWidget(self.label_3,2,0,1,1)

        self.cbRocks = QtGui.QCheckBox(Dialog)
        self.cbRocks.setChecked(True)
        self.cbRocks.setObjectName("cbRocks")
        self.gridlayout.addWidget(self.cbRocks,3,2,1,1)
        self.vboxlayout.addLayout(self.gridlayout)

        spacerItem1 = QtGui.QSpacerItem(422,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem1)

        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.vboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),Dialog.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.txtArtist,self.txtAlbum)
        Dialog.setTabOrder(self.txtAlbum,self.txtSong)
        Dialog.setTabOrder(self.txtSong,self.cbRocks)
        Dialog.setTabOrder(self.cbRocks,self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Artist", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Album", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Song", None, QtGui.QApplication.UnicodeUTF8))
        self.cbRocks.setText(QtGui.QApplication.translate("Dialog", "I like it (unchecked: I don\'t like it)", None, QtGui.QApplication.UnicodeUTF8))

