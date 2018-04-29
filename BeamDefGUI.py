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
from spiwrite import AwmfCommander, SpiInitException, SB_MODE, TX_MODE, RX_MODE

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

        #Repeatedly check for spi interposer board
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tryConnectSPI)
        self.timer.start(1000)

        #Connect inputs
        self.thetaBox.valueChanged.connect(self.setCsVector)
        self.phiBox.valueChanged.connect(self.setCsVector)
        self.beamDefButton.clicked.connect(self.calcBeamDef)
        self.programButton.clicked.connect(self.progSpi)

        #initial view
        self.setCsVector()
    
    def tryConnectSPI(self):
        print("Tick")
        if self.spiConnected:
            return
        try:
            AwmfCommander.initSpi() 
            self.spiConnected = True
            self.spiStatusLabel.setText("") #remove "not detected" label
        except SpiInitException:
            self.spiStatusLabel.setText("SPI interposer not detected")
            self.spiConnected = False
            self.programButton.setEnabled(False)

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

    def getBeamAmp(self):
        return self.amplitudeBox.value()
    
    def calcBeamDef(self):
        """prints the new beam settings based off the input frequency, theta, and
        phi"""
        #self.beamDef = BeamDefinition(self.thetaO(), self.phiO(), self.calculateWavelength(), beamStrength=self.getBeamAmp())
        #self.phaseSettings = self.beamDef.getPhaseSettings()

        #self.glViewer.setAFPoints((self.beamDef.generateAllAF()))
        self.beamDef = BeamDefinition(self.thetaO(), self.phiO(), self.calculateWavelength(), beamStrength=self.getBeamAmp())
        self.phaseSettings = self.beamDef.getPhaseSettings()
        self.glViewer.setCurrentSettingVector(self.thetaO(), self.phiO())

        #update status label
        statusString = "("
        labels = ["NE", "SE", "SW", "NW"]
        for s in range(len(self.phaseSettings)):
            statusString += (labels[s] + " = " + self.phaseSettings[s].__str__() + ", ")

        if self.radioButtonTx.isChecked():
            statusString += "TX mode"
        else:
            statusString += "RX mode"
        statusString += ("| Amp:" + self.beamDef.getBeamStrength().__str__())
        statusString += ")"
        
        self.curSettingsLabel.setText(statusString)
        if self.spiConnected:
            self.programButton.setEnabled(True)
        

    def setCsVector(self):
        #self.glViewer.setCurrentSettingVector(self.thetaO(), self.phiO())
        #self.beamDef = BeamDefinition(self.thetaO(), self.phiO(), self.calculateWavelength(), beamStrength=self.getBeamAmp())
        #self.phaseSettings = self.beamDef.getPhaseSettings()
        #use a temp calculation
        self.glViewer.setAFPoints( BeamDefinition(self.thetaO(), self.phiO(), self.calculateWavelength(), beamStrength=self.getBeamAmp()).generateAllAF() )

    def progSpi(self):
        mode = RX_MODE
        if self.radioButtonTx.isChecked():
            mode = TX_MODE

        #convert to awmf amplification settings here... subtract by 31
        try:
            AwmfCommander.setBeam(mode, self.phaseSettings[0], self.phaseSettings[1], self.phaseSettings[2], self.phaseSettings[3],
                31 - self.getBeamAmp(), 31 - self.getBeamAmp(), 31 - self.getBeamAmp(), 31 - self.getBeamAmp())
        except SpiInitException:
            self.spiStatusLabel.setText("SPI interposer not detected")
            self.spiConnected = False
            self.programButton.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()









