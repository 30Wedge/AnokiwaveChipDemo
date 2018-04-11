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
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication

from maingui import Ui_Dialog

import sys
from beamdef import BeamDefinition

class MyApp(QDialog, Ui_Dialog):
    
    def __init__(self):
        #QtGui.QMainWindow.__init__(self)
        super(MyApp, self).__init__()
        self.setupUi(self)
        self.BeamDef.clicked.connect(self.CalcBeamDef)
        #self.glViewer.quad(0,0,1,0,0,1,1,1)
        
    def CalculateWavelength(self):
        """this module takes in the frequency and speed of light to fight the
        Wavelength """
        Frequency = (self.waveLength.value()) * 100000000
        c = 3*100000000
        WaLength = c / Frequency
        return WaLength
    
    def PhiO(self):
        """takes in the value of Phi from the User"""
        PhiV = (self.phi.value())
        return PhiV
    
    def ThetaO(self):
        """takes in the value of Theta from the User"""
        ThetaV = (self.theta.value())
        return ThetaV
    
    def CalcBeamDef(self):
        """prints the new beam settings based off the input frequency, theta, and
        phi"""
        NewBeamDef = BeamDefinition(self.ThetaO(), self.PhiO(), self.CalculateWavelength())
        x = NewBeamDef.getPhaseSettings()
        print(x)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())










