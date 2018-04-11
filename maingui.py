# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'maingui.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(698, 444)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(480, 60, 181, 131))
        self.groupBox.setObjectName("groupBox")
        self.formLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.formLayoutWidget.setGeometry(QtCore.QRect(9, 10, 161, 81))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.labelTheta = QtWidgets.QLabel(self.formLayoutWidget)
        self.labelTheta.setObjectName("labelTheta")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.labelTheta)
        self.theta = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.theta.setMinimum(-360.0)
        self.theta.setMaximum(360.0)
        self.theta.setSingleStep(0.5)
        self.theta.setObjectName("theta")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.theta)
        self.labelPhi = QtWidgets.QLabel(self.formLayoutWidget)
        self.labelPhi.setObjectName("labelPhi")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.labelPhi)
        self.phi = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.phi.setMinimum(-360.0)
        self.phi.setMaximum(360.0)
        self.phi.setSingleStep(0.5)
        self.phi.setObjectName("phi")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.phi)
        self.labelWavelength = QtWidgets.QLabel(self.formLayoutWidget)
        self.labelWavelength.setObjectName("labelWavelength")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.labelWavelength)
        self.waveLength = QtWidgets.QDoubleSpinBox(self.formLayoutWidget)
        self.waveLength.setMinimumSize(QtCore.QSize(62, 0))
        self.waveLength.setMinimum(26.5)
        self.waveLength.setMaximum(30.0)
        self.waveLength.setSingleStep(0.1)
        self.waveLength.setObjectName("waveLength")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.waveLength)
        self.BeamDef = QtWidgets.QPushButton(self.groupBox)
        self.BeamDef.setGeometry(QtCore.QRect(10, 100, 161, 23))
        self.BeamDef.setObjectName("BeamDef")
        self.glViewer = QAntennaViewer(Dialog)
        #self.glViewer.setGeometry(QtCore.QRect(10, 10, 451, 411))
        self.glViewer.setObjectName("glViewer")
        self.programButton = QtWidgets.QPushButton(Dialog)
        self.programButton.setGeometry(QtCore.QRect(490, 310, 161, 111))
        self.programButton.setObjectName("programButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "Beam Direction"))
        self.labelTheta.setText(_translate("Dialog", "theta"))
        self.labelPhi.setText(_translate("Dialog", "phi"))
        self.labelWavelength.setText(_translate("Dialog", "wavelength"))
        self.BeamDef.setText(_translate("Dialog", "BeamDef"))
        self.programButton.setText(_translate("Dialog", "Send it"))

from qantennaviewer import QAntennaViewer
