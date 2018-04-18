import sys
import math
from math import sin, cos, radians
from collections import namedtuple

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
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    #3D, cartesian / 3D, polar object types
    Point3C = namedtuple('Point3C', ['x','y','z'])
    Point3P = namedtuple('Point3P', ['theta','phi','r'])

    def __init__(self, parent=None):
        super(QAntennaViewer, self).__init__(parent)

        self.substrate = 0
        self.beamPattern = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.lastPos = QPoint()

        self.trolltechGreen = QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.trolltechRed = QColor.fromCmykF(0.0, 1.0, 1.0, 0.0)
        self.trolltechBlue = QColor.fromCmykF(1.0, 1.0, 0.0, 0.0)
        self.trolltechPurple = QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)
        self.trolltechOrange = QColor.fromCmykF(0.39, 0.55, 0.88, 0.1)

        self.substrateColor = QColor.fromCmykF(0.57, 0, 0.76, 0.77)
        self.antennaColor = QColor.fromCmykF(0, 0.17, 0.93, 0.16)

        self.afPoints = [] 
        self.afNPhi = 0     #number of phi points
        self.afNTheta = 0   #number of theta points 

        self.dirtyBeamPattern = False #if true, redraw

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

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        #self.setAFPoints([4 * angle / (360 * 16)])
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def setAFPoints(self, afList, n_phi=30, n_theta=30):
        """expects a list of sorted (theta, phi, AF) points to plot 
            this antenna's AF

            n_phi = # of different values of phi
            n_theta = # of different values of theta

            Aught to be sorted by phi, then theta, least to greatest
            """
        if afList != self.afPoints:
            self.afPoints = afList
            self.afNPhi = n_phi
            self.afNTheta = n_theta
            self.dirtyBeamPattern = True
            self.update()

    def initializeGL(self):
        print(self.getOpenglInfo())

        self.setClearColor(self.trolltechPurple.darker())
        self.substrate = self.makeSubstrate()
        self.beamPattern = self.makeBeamPattern()
        gl.glShadeModel(gl.GL_FLAT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        #gl.glEnable(gl.GL_CULL_FACE)

    def paintGL(self):
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glTranslated(0.0, 0.0, -10.0)
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        gl.glCallList(self.substrate)
        if self.dirtyBeamPattern: #redraw if necessary
            self.beamPattern = self.makeBeamPattern()
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
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)

        self.lastPos = event.pos()

    def makeBeamPattern(self):
        """ Draws the beam pattern from self.afPoints 
            Expec"""
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)


        #scale factor
        m = 0.4 #????
        
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
                self.quad_a_3P(p1, p2, p3, p4)

            #get that last patch in this row by wrapping it around to the beginning
            p1 = self.Point3P(*self.afPoints[(theta + 0) * self.afNTheta + (phi + 1)])
            p2 = self.Point3P(*self.afPoints[(theta + 1) * self.afNTheta + (phi + 1)])
            p3 = self.Point3P(*self.afPoints[(theta + 1) * self.afNTheta + (0)])
            p4 = self.Point3P(*self.afPoints[(theta + 0) * self.afNTheta + (0)])
            self.setColor(self.AfToColor(p3.r))
            p1, p2, p3, p4 = [self.Point3P(p.theta, p.phi, m*p.r) for p in (p1,p2,p3,p4)]
            self.quad_a_3P(p1, p2, p3, p4)

        #End GL point list
        gl.glEnd()
        gl.glEndList()

        return genList
    
    def P3toC3(self, pol):
        """
            polar to cartesian 

            There's definitely some superior built-in way to do this.
                I'll find it and figure that out if this turns out to be too slow

            pol - Point3P(phi, theta, r)
            return- Point3C(x,y,z)
        """

        x = sin(radians(pol.phi)) * sin(radians(pol.theta)) * pol.r
        y = cos(radians(pol.phi)) * sin(radians(pol.theta)) * pol.r
        z = cos(radians(pol.theta)) * pol.r 
        return self.Point3C(x,y,z)

    def AfToColor(self, af):
        """0 <= af <= 1"""
        h = 240 - (af * 240)
        return QColor.fromHsl(h,200,182, .4)

    def makeSubstrate(self):
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)

        #m = scale factor
        m = 0.02
        #hardcode units match the hfss model in mm
        #self.drawAntennaGrid( m*5.4, 4, 1, m*3.4, m* 4.2, m*0.5)
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

        ##Draw the substrate centered on the origin with back at z=0
        self.setColor(self.substrateColor)
        self.prism(-sub_x/2, -sub_y/2, 0, sub_x, sub_y, sub_z)

        ##draw patchAntennas
        self.setColor(self.antennaColor)
        #Figure out how to space patches
        #start drawing from -x, -y
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
        self.quad_a(x, y1, z1, x, y1 + y_len, z1, x, y1 + y_len, z1 + z_len, x, y1, z1 + z_len)

    def rect_y(self, y, x1, z1, x_len, z_len):
        """Defines a rectangle orthogonal to the y direction"""
        self.quad_a(x1, y, z1, x1 + x_len, y, z1, x1 + x_len, y, z1 + z_len, x1, y, z1 + z_len)

    def rect_z(self, z, x1, y1, x_len, y_len):
        """Defines a rectangle orthogonal to the z direction"""
        self.quad_a(x1, y1, z, x1 + x_len, y1, z, x1 + x_len, y1 + y_len, z, x1, y1 + y_len, z)

    ##Quad family -- draw _a_rbitrary rectangles in space 

    def quad_a_3P(self, p1, p2, p3, p4):
        """Take Point3P namedtuples instead"""
        self.quad_a_3C(self.P3toC3(p1), self.P3toC3(p2), self.P3toC3(p3), self.P3toC3(p4))

    def quad_a_3C(self, p1, p2, p3, p4):
        """Take Point3C namedtuples instead"""
        self.quad_a(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z, p3.x, p3.y, p3.z, p4.x, p4.y, p4.z)

    def quad_a(self, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4):
        """exhaustively defines all 4 points of a quadrangle and draws it"""
        gl.glVertex3d(x1, y1, z1)
        gl.glVertex3d(x2, y2, z2)
        gl.glVertex3d(x3, y3, z3)
        gl.glVertex3d(x4, y4, z4) 

    def normalizeAngle(self, angle):
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
############ below is for testing only
########################################################################



class Window(QWidget):
    """Dummy container class for testing copy paste from 
      https://github.com/baoboa/pyqt5/tree/master/examples/opengl
      """
    def __init__(self, beamViewTest=True):
        super(Window, self).__init__()

        self.glWidget = QAntennaViewer()

        self.xSlider = self.createSlider()
        self.ySlider = self.createSlider()
        self.zSlider = self.createSlider()

        self.xSlider.valueChanged.connect(self.glWidget.setXRotation)
        self.glWidget.xRotationChanged.connect(self.xSlider.setValue)
        self.ySlider.valueChanged.connect(self.glWidget.setYRotation)
        self.glWidget.yRotationChanged.connect(self.ySlider.setValue)
        self.zSlider.valueChanged.connect(self.glWidget.setZRotation)
        self.glWidget.zRotationChanged.connect(self.zSlider.setValue)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        mainLayout.addWidget(self.xSlider)
        mainLayout.addWidget(self.ySlider)
        mainLayout.addWidget(self.zSlider)
        self.setLayout(mainLayout)

        self.xSlider.setValue(15 * 16)
        self.ySlider.setValue(345 * 16)
        self.zSlider.setValue(0 * 16)

        self.setWindowTitle("QAntennaViewer")

        if beamViewTest:
            b = BeamDefinition(20, 15, 0.01)
            pts = b.generateAllAF()
            self.glWidget.setAFPoints(pts)

    def createSlider(self):
        slider = QSlider(Qt.Vertical)

        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)

        return slider


if __name__ == '__main__':

    from beamdef import BeamDefinition

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
