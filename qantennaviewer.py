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
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    #3D, cartesian / 3D, polar object types
    Point3C = namedtuple('Point3C', ['x','y','z'])
    Point3P = namedtuple('Point3P', ['theta','phi','r']) #degrees

    def __init__(self, parent=None):
        super(QAntennaViewer, self).__init__(parent)

        #OpenGL call lists
        self.substrate = 0
        self.beamPattern = 0
        self.axisLines = 0
        self.currentSettings = 0

        self.xRot = 0
        self.yRot = 0
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

        self.dirtyBeamPattern = False #if true, recalculate antenna pattern points
        self.dirtyCurrentSettings = True

        #current setting vector
        self.csTheta = 10
        self.csPhi = 10
        self.csBeamScale = 1.0

        #draw options
        self.drawAxis = True 


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
        #0.5 just emperically work
        if theta != self.csTheta or phi != self.csPhi or beamStrength != self.csBeamScale:
          self.dirtyCurrentSettings = True
          self.csBeamScale =  beamStrength
          self.csPhi = phi
          self.csTheta = theta

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
        gl.glTranslated(0.0, 0.0, -10.0)
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        #gl.glCallList(self.substrate)
        if self.drawAxis:
            pass
            gl.glCallList(self.axisLines)
        if self.dirtyBeamPattern: #redraw if necessary
            self.beamPattern = self.makeBeamPattern()
            self.dirtyBeamPattern = False
        if self.dirtyCurrentSettings:
            self.currentSettings = self.makeCurrentSettings()
            self.dirtyCurrentSettings = False
        gl.glCallList(self.currentSettings)
        #gl.glCallList(self.beamPattern)

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
        m = self.afBeamScale #????
        
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
            pol - Point3P(phi, theta, r)
            return- Point3C(x,y,z)
        """
        assert(isinstance(pol, self.Point3P))
        x = sin(radians(pol.phi)) * sin(radians(pol.theta)) * pol.r
        y = cos(radians(pol.phi)) * sin(radians(pol.theta)) * pol.r
        z = cos(radians(pol.theta)) * pol.r 
        return self.Point3C(x,y,z)
    def C3toP3(self, c, theta0=Point3C(0,0,1), phi0=Point3C(0,1,0),O0=Point3C(0,0,0)):
      """ PointC3 to PointP3"""
      t = self.angBtwC(c, theta0)
      p = self.angBtwC(c, phi0)
      r = self.subC(c, O0)
      return self.Point3C(t, p, r)
      assert(isinstance(c, self.Point3C))


    def P3toNewP3(self, pP0, phi1, theta1, O1, phi0=Point3C(0,1,0), theta0=Point3C(0,0,1), O0=Point3C(0,0,0))
      """ Converts P3 in one cordinate system to new coordinate system
        pP0 - Polar point in old coordinate space

        phi1 = C vector pointing in new phi=0 direction
        theta1 = C vector pointing in new theta=0 direction
        O1 = C vector definining new origin
        
        ...0 - definition of old coordinate space
      """
      pc =self.P3toC3(pP0)

      #TODO shift coordinates properly
      
      t_new = self.angBtwC(pc, theta1)
      phi_new = self.angBtwC(pc, phi1)
      r_new = self.subC(pc, O1)
      return self.PointP3(t_new, phi_new, r_new)

    def angBtwC(self, C1, C2):
      """gets the angle between C1 and C2"""
      return acos( (self.dotC(C1, C2)) / (self.magC(C1) * self.magC(C2)))

    def dotC(self, C1, C2):
      return C1.x * C2.x + C1.y * C2.y + C1.z * C2.z

    def normC(self, C):
      """Normalization of C"""
      a = self.magC(C)
      return self.Point3C(C.x / a, C.y / a, C.z / a)

    def subC(self, C1, C2):
      return self.Point3C(C1.x - C2.x, C1.y - C2.y, C1.z - C2.z)

    def magC(self, C):
      """magnitude of Point3C"""
      return math.sqrt(C.x **2 + C.y ** 2 + C.z ** 2)

    def AfToColor(self, af):
        """0 <= af <= 1"""
        h = 240 - (af * 240)
        return QColor.fromHsl(h,200,182, self.beamTransparancy)

    def drawVector(self, p3c_s, p3c_p, color, arrow=True, ar=.1, aw=10, a_n=4):
        """Draw a vector from s to p.
          Assume you're working with GL_LINES

          Optional parameters are for putting an arrow head at the end 
        """

        self.setColor(color)
        p1 = self.P3toC3(p3c_s)
        p2 = self.P3toC3(p3c_p)
        self.glVertex_C3(p1)
        self.glVertex_C3(p2)

        if arrow:
          ptList = []
          for i in range(a_n):
            ptList.append(self.Point3P(aw, i * ((360)/a_n), p3c_p.r - ar))

          print(len(ptList),ptList)
          ptList = map(self.P3toC3,ptList )
          c = zip(ptList, cycle([p2]))
          for p in c:
            self.glVertex_C3(p[0])
            self.glVertex_C3(p[1])

    def makeCurrentSettings(self):
        """ Draw vector showing current input settings"""
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)
        gl.glBegin(gl.GL_LINES)
        #use afBeamScale for r
        self.drawVector(self.Point3P(0,0,0), self.Point3P(self.csTheta,self.csPhi, 0.1 + self.csBeamScale * self.afBeamScale), self.csColor, arrow=True)
        gl.glEnd()
        gl.glEndList()
        return genList

    def makeAxisLines(self):
        """Draw axis lines"""
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)

        gl.glBegin(gl.GL_LINES)

        self.drawVector(self.Point3P(0,0,0), self.Point3P(0,0,10), self.zAxisBlue, arrow=False)
        self.drawVector(self.Point3P(90,0,0), self.Point3P(90,0,10), self.yAxisGreen, arrow=False)
        self.drawVector(self.Point3P(90,90,0), self.Point3P(90,90,10), self.xAxisRed, arrow=False)

        gl.glEnd()
        gl.glEndList()

        return genList

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

    def glVertex_C3(self, point3p):
      gl.glVertex3d(point3p.x, point3p.y, point3p.z)

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
            b = BeamDefinition(10, 10, 0.01)
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
