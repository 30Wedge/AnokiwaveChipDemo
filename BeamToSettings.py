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

from math import sin, cos, pow, e, pi, radians, trunc, degrees
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
      [[x],[],[x][x]], maxAf """

    self.theta = radians(theta) #math module functions use radians
    self.phi = radians(phi)
    self.beamStrength = beamStrength
    self.waveLength = waveLength

    #AWMF-0108 constants
    self.phaseControlRange = 32
    self.gainControlRange = 32

    self.phaseControlMax = 2 * pi; #radians
    self.gainControlMax = 1; #??? check units on this

    self.antennaGridSize = {}
    self.antennaGridSize['x'] = 2
    self.antennaGridSize['y'] = 2

  def maxArrayFactor(self):
    """
      returns:  array containing the phase offset for each antenna 
                to point at the specified theta/phi direction in awmf-0108 settings

                [ [NW , NE],
                  [SW , SE]]
    """
    k = 2 * pi / (self.waveLength) # wave number
    
    ##TODO phi/theta to ew/ns angle the real way
    ew_angle = self.phi
    nw_angle = self.theta

    ##TODO take d in properly
    d = 5 * pow(10,-3) 

    #calculate offsets between elements
    ew_phaseOffset = -k * d * sin(ew_angle);
    ns_phaseOffset = -k * d * sin(nw_angle);

    ##Calculate offsets for each element
    #inifialize offset list with zeros
    offsets = [ [0 for x in range(self.antennaGridSize['x'])] for y in range(self.antennaGridSize['y'])]
    for i in range(0, self.antennaGridSize['x']):
      # add ns offset between rows
      if i == 0:
        offsets[0][0] = 0
      else:
        offsets[i][0] = offsets[i-1][0] + ns_phaseOffset
      
      # add ew offset between columns
      for j in range(1, self.antennaGridSize['y']):
        offsets[i][j] = offsets[i][j - 1] + ew_phaseOffset

    #normalize the offset array to settings
    n_offsets = map(lambda x: map(lambda y: self._radiansToAwmf0108(y), x), offsets) 

    #TODO calculate Array factor
    af = 1
    return n_offsets, af



  def fullArrayFactor(self, d_theta):
    """
      returns:  array containing the AF for the particular settings at every
                spherical point spaced d_theta apart from one another
    """
    pass #TODO

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
  d1 = b1.maxArrayFactor()
  print "BeamDefinition(15, 20, w, 1) "
  print d1.__str__() + "\n"

  b2 = BeamDefinition(15, -20, w, 1) 
  d2 = b2.maxArrayFactor()
  print "BeamDefinition(15, -20, w, 1) "
  print d2.__str__()  + "\n"

  b3 = BeamDefinition(-10, -120, w, 1) 
  d3 = b3.maxArrayFactor()
  print "BeamDefinition(-10, -120, w, 1) "
  print d3.__str__()  + "\n"

  #--------------------------------------
  ##with 0 and 0 you'd expect even phase offset
  bUniform = BeamDefinition(0, 0, w, 1)
  dU, x = bUniform.maxArrayFactor()
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
