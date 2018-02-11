#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        Beam Definition
# Purpose:     Convert from polar coordinates
#
# Author:      Andy MacGregor 
#
# Created:     1/12/2017
# Copyright:   (c) Anokiwave Capstone Team 2017
# Licence:     tbd by Anokiwave 
#-------------------------------------------------------------------------------

from math import sin, cos, atan, pow, e, pi, radians, trunc, degrees
from cmath import exp

class BeamDefinition:
  """ Calculates AWMF phase settings from beam definition
  
  Give it spherical coordinates, and it can return the AWMF-0108 phase settings
  """

  #speed of light
  C = 299792458

  def __init__(self, theta, phi, waveLength, beamStrength=None):
    """Inits the object with polar coordinate input 
    theta           polar angle offset in degrees
    phi             azimuth angle offset in degrees
    waveLength      ...
    beamStrength    useless for now. leave blank.

    A = BeamDefinition(theta, phi, wavelength) 

    A.maxArrayFactor()
      [[x, x],[x, x]], maxAf """

    self.theta = radians(theta) #math module functions use radians
    self.phi = radians(phi)
    self.beamStrength = beamStrength
    self.waveLength = waveLength

    #AWMF-0108 constants
    self.phaseControlRange = 32
    self.gainControlRange = 32
    self.phaseControlMax = 2 * pi; #radians
    self.gainControlMax = 1; #???TODO check units on this

    #Antenna parameters
    self.antennaGridSize = (2, 2) # (x, y)
    self.antennaSpacing = 5 * pow(10,3) #TODO check if this is correct

    #Calculated awmf0108 settings... calculate when needed
    self.phaseSettings = []
    self.gainSettings = []

  def getPhaseSettings(self):
    """
      returns:  array containing the phase offset for each antenna 
                to point at the specified theta/phi direction in awmf-0108 settings
                
                returns an xdim by ydim array of the phase settings

                ex. 2x2:
                [ [NW , NE],
                  [SW , SE]]

                ex. 1x4:
                [ [1, 2, 3, 4]]
    """
    #if they've already been calculated, don't redo the work
    if len(self.phaseSettings) > 0:
      return self.phaseSettings

    k = 2 * pi / (self.waveLength) # wave number
    
    ##phi/theta to ew/ns angle 
    #Project a 3d angle onto a 2d plane...
    p=self.phi
    t=self.theta 
    ew_angle = atan( sin(p) * sin(t) / cos(t) )
    nw_angle = atan( cos(p) * sin(t) / cos(t) )

    d = self.antennaSpacing

    ##calculate offsets between elements    
    ew_phaseOffset = -k * d * sin(ew_angle);
    ns_phaseOffset = -k * d * sin(nw_angle);

    ##Calculate offsets for each element
    #inifialize offset list with zeros
    offsets = [ [0 for x in range(self.antennaGridSize[0])] for y in range(self.antennaGridSize[1])]
    for i in range(0, self.antennaGridSize[0]):
      # add ns offset between rows
      if i == 0:
        offsets[0][0] = 0
      else:
        offsets[i][0] = offsets[i-1][0] + ns_phaseOffset
      
      # add ew offset between columns
      for j in range(1, self.antennaGridSize[1]):
        offsets[i][j] = offsets[i][j - 1] + ew_phaseOffset

    #normalize the offset array to settings
    n_offsets = map(lambda x: map(lambda y: self._radiansToAwmf0108(y), x), offsets) 
    
    self.phaseSettings = n_offsets

    return n_offsets

  def getGainSettings(self):
    """ 
      Return gain settings for this configuration.
      As long as we're using uniform illumination, set it all to 1
    """
    if len(self.gainSettings > 0) :
      return self.gainSettings

    xdim = self.antennaGridSize[0]
    ydim = self.antennaGridSize[1]
    self.gainSettings = [[1 for x in range(xdim)] for y in range(ydim)]

    return self.gainSettings

  def loadNewAntennaParameters(self, gridX, gridY, spacing):
    """ 
      Replaces the default antenna parameters with ones specified by the user.
    """
    self.antennaGridSize = (gridX, gridY)
    self.antennaSpacing  = spacing

    #force recalulation of gain and phase settings
    self.phaseSettings = []
    self.gainSettings = []
    return

  def visualiseGrid(self, d_theta, d_phi):
    """
      d_theta: difference between AF test points (in degrees)

      returns:  a list of tuples to graph (theta, phi, AF)
    """
    #iterate from theta = 0 to 180 and phi = 0 to 360 in increments of d_theta and d_phi
    t = 0
    p = 0

    points = []
    while t < 180 :
      while p < 180 :
        # calculate the Antenna Factor for this angle at these settings and add it
        # to the list
        a = _calculateArrayFactor(radians(t), radians(p), 
          self.getGainSettings(), self.getPhaseSettings(), self.waveLength);
        points.append( (t, p, a) )

        p = p + d_phi
      t = t + d_theta

    return points

  def _calculateArrayFactor(self, theta, phi, I, d, waveLength):
    """ 
    private: calculate the strength of a configuratio at angle theta/phi
    on a square plane antenna array.
    
    I:  2D array of amplitudes of each element in square array
    d:  2D array of phases of each element in square array
      **Must have dimensions self.antennaGridSize
    
    return: scalar ArrayFactor (not normalized)
    """

    dist = self.antennaSpacing #TODO this formula's units and my units don't line up. Fix
    k = 2 * pi / waveLength # k = wave numer
    
    cumulativeAF = 0
    for n in range(0, self.antennaGridSize[0]):
      for m in range(0, self.antennaGridSize[1]):
        #exponential term to calculate AF
        cumulativeAF += I[n][m] * exp(1j *(d[n][m] + 
          k*dist*n*sin(theta)*cos(phi) + 
          k*dist*m*sin(theta)*sin(phi)))

    return cumulativeAF

  ###Helper-funciton-land
  def _radiansToAwmf0108(self, rads):
    """
      rads: angle in radians to convert
      return: phase setting in awmf-0108 format
    """
    interval = self.phaseControlMax / self.phaseControlRange
    
    #fix to be in range between 0 and 2pi radians
    fixed = rads % (2*pi)

    return trunc(self._roundToNearest(fixed, interval) / interval);

  def _roundToNearest(self, x, multiple):
    """
      round x to the nearest multiple of _multiple_
      credit to stackOverflow
    """
    return multiple * round( float(x) / multiple)

def test():
  """Test harness for this module """
  #Does some test calculations to make sure the module functions
  f = 28 * pow(10,9) #29GHz
  c = 3 * pow(10, 8)
  w = c/f 

  #----------------------------------
  ## Basic tests to see different outputs
  b1 = BeamDefinition(15, 20, w, 1) 
  d1 = b1.getPhaseSettings()
  print "BeamDefinition(15, 20, w, 1) "
  print d1.__str__() + "\n"

  b2 = BeamDefinition(15, -20, w, 1) 
  d2 = b2.getPhaseSettings()
  print "BeamDefinition(15, -20, w, 1) "
  print d2.__str__()  + "\n"

  b3 = BeamDefinition(-10, -120, w, 1) 
  d3 = b3.getPhaseSettings()
  print "BeamDefinition(-10, -120, w, 1) "
  print d3.__str__()  + "\n"

  #--------------------------------------
  ##with 0 and 0 you'd expect even phase offset
  bUniform = BeamDefinition(0, 0, w, 1)
  dU = bUniform.getPhaseSettings()
  print "BeamDefinition(0, 0, w, 1)"
  print dU.__str__()  + "\n"

  assert dU[0][0] == dU[0][1] == dU[1][0] == dU[1][1]
  #TODO Create some test cases with other values that you can assert


if __name__ == '__main__':
  from time import time
  t1 = time()
  test()
  t2 = time()
  tt = t2 - t1
  print "Total time elapsed: " + tt.__str__() + "s"
