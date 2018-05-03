#-------------------------------------------------------------------------------
# Name:        qantennaviewer
# Purpose:     Draw antenna and radiation patterns
#
# Author:      Andy MacGregor
#              
#
# Created:     12/12/2017
# Copyright:   (c) Anokiwave Capstone Team 2017
# Licence:     <LGPLv3>
#   See        https://www1.qt.io/qt-licensing-terms/
#              https://www.qt.io/download
#-------------------------------------------------------------------------------

import sys
import math
from math import sin, cos, radians, acos
from collections import namedtuple
from itertools import cycle

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
        QWidget)
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor

import OpenGL.GL as gl
#import OpenGL.GLU as glu

class QAntennaViewer(QOpenGLWidget):
    """draws the antenna plus radiation pattern in this openGL widget
      Barely forked from a hello world example
      """
    xRotationChanged = pyqtSignal(int)
    zoomChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    #3D, cartesian / 3D, polar object types
    Point3C = namedtuple('Point3C', ['x','y','z'])
    Point3P = namedtuple('Point3P', ['theta','phi','r']) #degrees

    def __init__(self, parent=None, cst0=0, csp0=0, csbs0=1.0):
        super(QAntennaViewer, self).__init__(parent)

        #OpenGL call lists
        self.substrate = 0
        self.beamPattern = 0
        self.axisLines = 0
        self.currentSettings = 0

        self.xRot = 0
        self.zoom = 1.0
        self.zRot = 0

        self.lastPos = QPoint()

        self.xAxisRed = QColor.fromCmykF(0.0, 1.0, 1.0, 0.18)
        self.yAxisGreen = QColor.fromCmykF(1.0, 0.0, 1.0, 0.21)
        self.zAxisBlue = QColor.fromCmykF(1.0, 1.0, 0.0, .19)
        self.csColor = QColor.fromCmykF(0.29, 0.32, 0, 0.71)
        self.backgroundPurple = QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)
        

        self.substrateColor = QColor.fromCmykF(0.57, 0, 0.76, 0.77)
        self.antennaColor = QColor.fromCmykF(0, 0.17, 0.93, 0.16)

        #Drawn antenna factor pattern
        self.afPoints = [] 
        self.afNPhi = 0     #number of phi points
        self.afNTheta = 0   #number of theta points
        self.afBeamScale = 0.5
        self.beamTransparancy = 200

        self.dirtyBeamPattern = False 
        self.dirtyCurrentSettings = True
        self.dirtyAntennaBox = True

        #current setting vector
        self.csTheta = cst0
        self.csPhi = csp0
        self.csBeamScale = csbs0

        #draw options
        self.drawAxis = True 
        self.antenna4x1 = True

    def setAntenna4x1(self, antenna4x1):
      """ True = draw 4x1 antenna
          False = draw 2x2 antenna"""
      self.dirtyAntennaBox = True
      self.antenna4x1 = antenna4x1
      self.update()

    def getOpenglInfo(self):
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
        """.format(
            gl.glGetString(gl.GL_VENDOR),
            gl.glGetString(gl.GL_RENDERER),
            gl.glGetString(gl.GL_VERSION),
            gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
        )

        return info

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def setCurrentSettingVector(self, theta, phi, beamStrength=1.0):
        """ Sets the direction of the current-settings pointing vector"""
        if theta != self.csTheta or phi != self.csPhi or beamStrength != self.csBeamScale:
          self.dirtyCurrentSettings = True
          self.csBeamScale =  beamStrength
          self.csPhi = phi
          self.csTheta = theta
          self.update()

    def setXRotation(self, angle):
        """Rotation is limited from -90 to 90 degrees """
        angle = self.normalizeAngle(angle)
        if angle > 90*16:
          return
        if angle != self.xRot:
            self.xRot = angle
            if angle >= 270*16:
              self.xRotationChanged.emit(angle - 360*16)
            else:
              self.xRotationChanged.emit(self.normalizeAngle(angle))
            self.update()

    def setZoom(self, zoom):
        z_c = zoom/100.0 + 0.1
        if z_c != self.zoom:
            self.zoom = z_c
            self.zoomChanged.emit(zoom)
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def setAFPoints(self, afList, n_phi=30, n_theta=30, beamStrength=1.0):
        """expects a list of sorted (theta, phi, AF) points to plot 
            this antenna's AF

            n_phi = # of different values of phi
            n_theta = # of different values of theta
            
            beamStrength = drawn magnitude of beam, from 0 to 1
            Aught to be sorted by phi, then theta, least to greatest
            """
        if beamStrength > 1:
          beamStrength = 1
        elif beamStrength < 0:
          beamStrength = 0

        if afList != self.afPoints:
            self.afPoints = afList
            self.afNPhi = n_phi
            self.afNTheta = n_theta
            #0.5 just works well for scale
            self.afBeamScale = 0.5 * beamStrength
            self.dirtyBeamPattern = True
            self.update()

    def initializeGL(self):
        print(self.getOpenglInfo())

        self.setClearColor(self.backgroundPurple.darker())
        self.substrate = self.makeSubstrate()
        self.beamPattern = self.makeBeamPattern()
        self.axisLines = self.makeAxisLines()
        gl.glShadeModel(gl.GL_FLAT)
        gl.glEnable(gl.GL_DEPTH_TEST)

        #enable alpha channel
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        #make prettier lines 
        gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
        gl.glEnable(gl.GL_LINE_SMOOTH)

    def paintGL(self):
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glTranslated(0.0, 0.0, -13.0)
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        #gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        gl.glTranslated(0.0, 0.0, -0.3)
        gl.glScale(self.zoom, self.zoom, self.zoom)
        if self.dirtyAntennaBox:
            self.substrate = self.makeSubstrate()
            self.dirtyAntennaBox = False
        if self.drawAxis:
            pass
            gl.glCallList(self.axisLines)
        if self.dirtyBeamPattern: #redraw if necessary
            self.beamPattern = self.makeBeamPattern()
            self.dirtyBeamPattern = False
        if self.dirtyCurrentSettings:
            self.currentSettings = self.makeCurrentSettings()
            self.dirtyCurrentSettings = False
        gl.glCallList(self.substrate)
        gl.glCallList(self.currentSettings)
        gl.glCallList(self.beamPattern)

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        gl.glViewport((width - side) // 2, (height - side) // 2, side,
                           side)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0) #sets perspective matrix
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
        elif event.buttons() & Qt.RightButton:
            self.setZRotation(self.zRot + 8 * dx)

        self.lastPos = event.pos()

    def makeBeamPattern(self):
        """ Draws the beam pattern from self.afPoints 
            Expec"""
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)


        #scale factor
        m = self.afBeamScale
        
        #collect points from self.afPoints
        for theta in range(self.afNTheta - 1):
            for phi in range(self.afNPhi - 1):
                
                #corners in polar coordinate -- converting them to Point3P s
                p1 = self.Point3P(*self.afPoints[(theta + 0) * self.afNTheta + (phi + 0)])
                p2 = self.Point3P(*self.afPoints[(theta + 1) * self.afNTheta + (phi + 0)])
                p3 = self.Point3P(*self.afPoints[(theta + 1) * self.afNTheta + (phi + 1)])
                p4 = self.Point3P(*self.afPoints[(theta + 0) * self.afNTheta + (phi + 1)])

                #key off of p3 arbitrarily
                self.setColor(self.AfToColor(p3.r))

                #scale AF with m
                p1, p2, p3, p4 = [self.Point3P(p.theta, p.phi, m*p.r) for p in (p1,p2,p3,p4)]

                #draw this patch
                self.quad3P(p1, p2, p3, p4)

            #get that last patch in this row by wrapping it around to the beginning
            p1 = self.Point3P(*self.afPoints[(theta + 0) * self.afNTheta + (phi + 1)])
            p2 = self.Point3P(*self.afPoints[(theta + 1) * self.afNTheta + (phi + 1)])
            p3 = self.Point3P(*self.afPoints[(theta + 1) * self.afNTheta + (0)])
            p4 = self.Point3P(*self.afPoints[(theta + 0) * self.afNTheta + (0)])
            self.setColor(self.AfToColor(p3.r))
            p1, p2, p3, p4 = [self.Point3P(p.theta, p.phi, m*p.r) for p in (p1,p2,p3,p4)]
            self.quad3P(p1, p2, p3, p4)

        gl.glEnd()
        gl.glEndList()

        return genList
    
    def P3toC3(self, pol):
        """
            pol - Point3P(phi, theta, r)
            return- Point3C(x,y,z)
        """
        assert(isinstance(pol, self.Point3P))
        x = sin(radians(pol.phi)) * sin(radians(pol.theta)) * pol.r
        y = cos(radians(pol.phi)) * sin(radians(pol.theta)) * pol.r
        z = cos(radians(pol.theta)) * pol.r 
        return self.Point3C(x,y,z)
    
    def AfToColor(self, af):
        """0 <= af <= 1"""
        h = 240 - (af * 240)
        return QColor.fromHsl(h,200,182, self.beamTransparancy)

    def drawVector(self, p3c_s, p3c_p, color):
        """Draw a vector from s to p.
          Assume you're working with GL_LINES
        """
        self.setColor(color)
        p1 = self.P3toC3(p3c_s)
        p2 = self.P3toC3(p3c_p)
        self.glVertexC3(p1)
        self.glVertexC3(p2)

    def makeCurrentSettings(self):
        """ Draw vector showing current input settings"""
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)
        gl.glBegin(gl.GL_LINES)
        #use afBeamScale for r
        self.drawVector(self.Point3P(0,0,0), self.Point3P(self.csTheta,self.csPhi, 0.1 + self.csBeamScale * self.afBeamScale), self.csColor)
        gl.glEnd()
        gl.glEndList()
        return genList

    def makeAxisLines(self):
        """Draw axis lines"""
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_LINES)

        self.drawVector(self.Point3P(0,0,0), self.Point3P(0,0,10), self.zAxisBlue)
        self.drawVector(self.Point3P(90,0,0), self.Point3P(90,0,10), self.yAxisGreen)
        self.drawVector(self.Point3P(90,90,0), self.Point3P(90,90,10), self.xAxisRed)

        gl.glEnd()
        gl.glEndList()

        return genList

    def makeSubstrate(self):
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)

        #m = scale factor -- 0.02 was found to work well
        m = 0.02
        #hardcode units match the real HFSS antenna model in mm
        if self.antenna4x1:
          self.drawAntennaGrid( m*5.4, 4, 1, m*3.4, m* 4.2, m*0.5)
        else:
          self.drawAntennaGrid( m*5.4, 2, 2, m*3.4, m* 4.2, m*0.5)

        #End GL point list
        gl.glEnd()
        gl.glEndList()

        return genList

    def drawAntennaGrid(self, spacing, dim_x, dim_y, patch_x, patch_y, sub_z=0.03):
        """Draw some antennas based on params
            units don't mean much
        """

        sub_x = dim_x * patch_x  + (dim_x + 0) * spacing
        sub_y = dim_y * patch_y  + (dim_y + 1) * spacing

        self.setColor(self.substrateColor)
        self.prism(-sub_x/2, -sub_y/2, 0, sub_x, sub_y, sub_z)

        self.setColor(self.antennaColor)
        space_x = spacing 
        space_y = spacing 

        start_x = -1 * ( ((dim_x-1)/2) * space_x  + patch_x/2)
        start_y = -1 * ( ((dim_y-1)/2) * space_y + patch_y/2)
        for i in range(dim_x):
            for j in range(dim_y):
                x = start_x + i*(space_x)
                y = start_y + j*(space_y)
                self.prism(x, y, sub_z, patch_x, patch_y, sub_z/4)



    def prism(self, x1, y1, z1, x_len, y_len, z_len):
        """Draws a prism orthogonal to the coordinate system"""
        #x faces
        self.rect_x(x1, y1, z1, y_len, z_len)
        self.rect_x(x1 + x_len, y1, z1, y_len, z_len)
        #y faces
        self.rect_y(y1, x1, z1, x_len, z_len)
        self.rect_y(y1 + y_len, x1, z1, x_len, z_len)
        #z faces
        self.rect_z(z1, x1, y1, x_len, y_len)
        self.rect_z(z1 + z_len, x1, y1, x_len, y_len)

    ##Rect family -- draw rectangles orthogonal to a given dimension

    def rect_x(self, x, y1, z1, y_len, z_len):
        """Defines a rectangle orthogonal to the x direction"""
        self.quad(x, y1, z1, x, y1 + y_len, z1, x, y1 + y_len, z1 + z_len, x, y1, z1 + z_len)

    def rect_y(self, y, x1, z1, x_len, z_len):
        """Defines a rectangle orthogonal to the y direction"""
        self.quad(x1, y, z1, x1 + x_len, y, z1, x1 + x_len, y, z1 + z_len, x1, y, z1 + z_len)

    def rect_z(self, z, x1, y1, x_len, y_len):
        """Defines a rectangle orthogonal to the z direction"""
        self.quad(x1, y1, z, x1 + x_len, y1, z, x1 + x_len, y1 + y_len, z, x1, y1 + y_len, z)

    ##Quad family -- draw arbitrary rectangles in space 

    def quad3P(self, p1, p2, p3, p4):
        """Take Point3P namedtuples instead"""
        self.quad3C(self.P3toC3(p1), self.P3toC3(p2), self.P3toC3(p3), self.P3toC3(p4))

    def quad3C(self, p1, p2, p3, p4):
        """Take Point3C namedtuples instead"""
        self.quad(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, p3.x, p3.y, p3.z, p4.x, p4.y, p4.z)

    def quad(self, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4):
        """exhaustively defines all 4 points of a quadrangle and draws it"""
        gl.glVertex3d(x1, y1, z1)
        gl.glVertex3d(x2, y2, z2)
        gl.glVertex3d(x3, y3, z3)
        gl.glVertex3d(x4, y4, z4) 

    def glVertexC3(self, point3p):
      gl.glVertex3d(point3p.x, point3p.y, point3p.z)

    def normalizeAngle(self, angle):
      #return angle % 360 * 16
      while angle < 0:
        angle += 360 * 16
      while angle > 360 * 16:
        angle -= 360 * 16
      return angle

    def setClearColor(self, c):
        gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())


########################################################################
############ Tests


class Window(QWidget):
    """Dummy container class for testing copy paste from 
      https://github.com/baoboa/pyqt5/tree/master/examples/opengl
      """
    def __init__(self):
        super(Window, self).__init__()

        self.glWidget = QAntennaViewer()

        #min = 1 prevents rapid flitching
        self.xSlider = self.createSlider(min=-90, max = 0)
        self.zSlider = self.createSlider()
        #change to zoom slide
        self.zoomSlider = self.createSlider(min=4, max= 9)

        self.xSlider.valueChanged.connect(self.glWidget.setXRotation)
        self.glWidget.xRotationChanged.connect(self.xSlider.setValue)
        self.zoomSlider.valueChanged.connect(self.glWidget.setZoom)
        self.glWidget.zoomChanged.connect(self.zoomSlider.setValue)
        self.zSlider.valueChanged.connect(self.glWidget.setZRotation)
        self.glWidget.zRotationChanged.connect(self.zSlider.setValue)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        mainLayout.addWidget(self.xSlider)
        mainLayout.addWidget(self.zSlider)
        mainLayout.addWidget(self.zoomSlider)
        self.setLayout(mainLayout)

        self.xSlider.setValue(45 * 16)
        #self.ySlider.setValue(0)
        self.zSlider.setValue(90 * 16)

        self.setWindowTitle("QAntennaViewer")

        beamViewTest = False
        antenna4x1Test = True

        if beamViewTest:
            b = BeamDefinition(10, 10, 0.01)
            pts = b.generateAllAF()
            self.glWidget.setAFPoints(pts)
        elif antenna4x1Test:
            b = BeamDefinition(40, 90, 0.01)
            self.glWidget.setCurrentSettingVector(40, 90)
            b.setAntenna( [[NE, NW, SE, SW]], [[ True, False, True, False]],5.4 * pow(10,-3))
            pts = b.generateAllAF()
            self.glWidget.setAntenna4x1(True)
            self.glWidget.setAFPoints(pts)

    def createSlider(self, min = 0, max=360):
        slider = QSlider(Qt.Vertical)

        slider.setRange(min * 16, max * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)

        return slider


if __name__ == '__main__':

    from beamdef import BeamDefinition, NE, NW, SE, SW

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
