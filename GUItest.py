# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUItest.ui'
#
# Created: Sun Feb 11 16:37:27 2018
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(1030, 911)
        self.phi = QtGui.QDoubleSpinBox(Dialog)
        self.phi.setGeometry(QtCore.QRect(310, 240, 61, 22))
        self.phi.setMinimum(-360.0)
        self.phi.setMaximum(360.0)
        self.phi.setSingleStep(0.5)
        self.phi.setObjectName(_fromUtf8("phi"))
        self.theta_2 = QtGui.QDoubleSpinBox(Dialog)
        self.theta_2.setGeometry(QtCore.QRect(310, 190, 61, 22))
        self.theta_2.setMinimum(-360.0)
        self.theta_2.setMaximum(360.0)
        self.theta_2.setSingleStep(0.5)
        self.theta_2.setObjectName(_fromUtf8("theta_2"))
        self.waveLength = QtGui.QDoubleSpinBox(Dialog)
        self.waveLength.setGeometry(QtCore.QRect(310, 290, 62, 22))
        self.waveLength.setMinimumSize(QtCore.QSize(62, 0))
        self.waveLength.setMinimum(26.5)
        self.waveLength.setMaximum(30.0)
        self.waveLength.setSingleStep(0.1)
        self.waveLength.setObjectName(_fromUtf8("waveLength"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(260, 190, 46, 13))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(260, 240, 46, 13))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(240, 290, 61, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.BeamDef = QtGui.QPushButton(Dialog)
        self.BeamDef.setGeometry(QtCore.QRect(290, 430, 75, 23))
        self.BeamDef.setObjectName(_fromUtf8("BeamDef"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "theta", None))
        self.label_2.setText(_translate("Dialog", "phi", None))
        self.label_3.setText(_translate("Dialog", "wavelength", None))
        self.BeamDef.setText(_translate("Dialog", "BeamDef", None))

