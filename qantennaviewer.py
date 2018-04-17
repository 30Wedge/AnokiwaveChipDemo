import sys
import math

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
        QWidget)
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor

import OpenGL.GL as gl
#import OpenGL.GLU as glu

class QAntennaViewer(QOpenGLWidget):
    """draws the antenna plus radiation pattern in this openGL widget
      Barley forked from a hello world example
      """
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

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

        self.afPoints = [2.0] #test as 2.0 for scale
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
        self.setAFPoints([4 * angle / (360 * 16)])
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

    def setAFPoints(self, afList):
        """expects a list of (theta, phi, AF) points to plot 
        this antenna's AF with"""
        if afList != self.afPoints:
            self.afPoints = afList
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
        gl.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
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
        genList = gl.glGenLists(2)
        gl.glNewList(genList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)

        print ("makeBeamPattern")
        #scale factor
        m = self.afPoints[0]
        self.drawAntennaGrid( m*0.034, 4, 1, m* 0.05, m* 0.06)
        
        #End GL point list
        gl.glEnd()
        gl.glEndList()

        return genList

    def makeSubstrate(self):
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_QUADS)

        #scale factor
        m = 2.0
        self.drawAntennaGrid( m*0.034, 1, 4, m* 0.05, m* 0.06)

        #End GL point list
        gl.glEnd()
        gl.glEndList()

        return genList

    def drawAntennaGrid(self, spacing, dim_x, dim_y, patch_x, patch_y, sub_z=0.03):
        """Draw some antennas"""

        sub_x = (dim_x ) * spacing + (dim_x+1) *patch_x
        sub_y = (dim_y ) * spacing + (dim_y+1)* patch_y

        #Draw the substrate centered on the origin with back at z=0
        self.setColor(self.substrateColor)
        self.prism(-sub_x/2, -sub_y/2, 0, sub_x, sub_y, sub_z)

        #draw patchAntennas
        self.setColor(self.antennaColor)
        #start drawing from -x, -y
        space_x = spacing - patch_x
        space_y = spacing - patch_y
        start_x = -((dim_x*patch_x)/2 + ((dim_x -1) * spacing / 2))
        start_y = -((dim_y*patch_y)/2 + ((dim_y -1) * spacing / 2))
        for i in range(dim_x):
            for j in range(dim_y):
                x = start_x + i*(spacing + patch_x)
                y = start_y + j*(spacing + patch_y)
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

    def rect_x(self, x, y1, z1, y_len, z_len):
        """Defines a rectangle orthogonal to the x direction"""
        self.quad_a(x, y1, z1, x, y1 + y_len, z1, x, y1 + y_len, z1 + z_len, x, y1, z1 + z_len)

    def rect_y(self, y, x1, z1, x_len, z_len):
        """Defines a rectangle orthogonal to the y direction"""
        self.quad_a(x1, y, z1, x1 + x_len, y, z1, x1 + x_len, y, z1 + z_len, x1, y, z1 + z_len)

    def rect_z(self, z, x1, y1, x_len, y_len):
        """Defines a rectangle orthogonal to the z direction"""
        self.quad_a(x1, y1, z, x1 + x_len, y1, z, x1 + x_len, y1 + y_len, z, x1, y1 + y_len, z)

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
    def __init__(self):
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

    def createSlider(self):
        slider = QSlider(Qt.Vertical)

        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)

        return slider

    def beamPlotterTest(self):
        pass 


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
