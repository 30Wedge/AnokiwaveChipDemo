#-------------------------------------------------------------------------------
# Name:        Beam definition GUI
# Purpose:
#
# Author:      Grayson Colwell
#
# Created:     11/02/2018
# Copyright:   (c) Anokiwave Capstone Team
# Licence:     Memes
#-------------------------------------------------------------------------------
import sys
from PyQt4 import QtCore, QtGui, uic
from BeamToSettings import BeamDefinition

qtCreatorFile = "GUItest.ui"

Ui_Dialog, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QDialog, Ui_Dialog):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_Dialog.__init__(self)
        self.setupUi(self)
        self.BeamDef.clicked.connect(self.CalcBeamDef)
    def CalculateWavelength(self):
        #this module takes in the frequency and speed of light to fight the
        #Wavelength
        Frequency = (self.waveLength.value()) * 100000000
        c = 3*100000000
        WaLength = c / Frequency
        return WaLength
    def PhiO(self):
        #takes in the value of Phi from the User
        PhiV = (self.phi.value())
        return PhiV
    def ThetaO(self):
        #takes in the value of Theta from the User
        ThetaV = (self.theta.value())
        return ThetaV
    def CalcBeamDef(self):
        #prints the new beam settings based off the input frequency, theta, and
        #phi
        NewBeamDef = BeamDefinition(self.ThetaO(), self.PhiO(), self.CalculateWavelength(), 10)
        x = NewBeamDef.getPhaseSettings()
        print x

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())










