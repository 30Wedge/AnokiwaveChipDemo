#-------------------------------------------------------------------------------
# Name:        Beam definition GUI
# Purpose:
#
# Author:      Grayson Colwell
#              Andy MacGregor
#
# Created:     11/02/2018
# Copyright:   (c) Anokiwave Capstone Team
# Licence:     Memes
#-------------------------------------------------------------------------------
import sys

from beamdef import BeamDefinition
from spiwrite import AwmfCommander, SpiInitException

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication
from maingui import Ui_Dialog



class MyApp(QDialog, Ui_Dialog):
    def __init__(self):
        super(MyApp, self).__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())

        self.beamDef = None
        self.phaseSettings = None

        self.spiConnected = False
        self.tryConnectSPI()

        #Connect inputs
        self.thetaBox.valueChanged.connect(self.setCsVector)
        self.phiBox.valueChanged.connect(self.setCsVector)
        self.beamDefButton.clicked.connect(self.calcBeamDef)
    
    def tryConnectSPI(self):
        #TODO real exception handling
        try:
            AwmfCommander.initSpi() 
            self.spiConnected = True
            self.spiStatusLabel.setText("") #remove "not detected" label
        except SpiInitException:
            self.spiStatusLabel.setText("SPI interposer not detected")
            self.spiConnected = False
            #TODO enable status box 

        return self.spiConnected

    def calculateWavelength(self):
        """this module takes in the frequency and speed of light to fight the
        Wavelength """
        Frequency = (self.waveLengthBox.value()) * pow(10,9)
        c = 3*pow(10,8)
        WaLength = c / Frequency
        return WaLength
    
    def phiO(self):
        """takes in the value of Phi from the User"""
        PhiV = (self.phiBox.value())
        return PhiV
    
    def thetaO(self):
        """takes in the value of Theta from the User"""
        ThetaV = (self.thetaBox.value())
        return ThetaV
    
    def calcBeamDef(self):
        """prints the new beam settings based off the input frequency, theta, and
        phi"""
        self.beamDef = BeamDefinition(self.thetaO(), self.phiO(), self.calculateWavelength())
        self.phaseSettings = self.beamDef.getPhaseSettings()

        self.glViewer.setAFPoints((self.beamDef.generateAllAF()))
        
        #update status label
        statusString = "("
        labels = ["NE", "SE", "SW", "NW"]
        for s in range(len(self.phaseSettings)):
            statusString += (labels[s] + " = " + self.phaseSettings[s].__str__() + ", ")

        if self.radioButtonTx.isChecked():
            statusString += "TX mode"
        else:
            statusString += "RX mode"
        statusString += ")"
        
        self.curSettingsLabel.setText(statusString)
        #TODO unlock send it button

    def setCsVector(self):
        self.glViewer.setCurrentSettingVector(self.thetaO(), self.phiO())


def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()









