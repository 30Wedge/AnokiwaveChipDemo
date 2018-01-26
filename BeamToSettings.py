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

from math import sin, cos, pow, e, pi, radians
from cmath import exp
class BeamDefinition:
  """ Calculates AWMF phase settings from beam definition
  
  Give it spherical coordinates, and it can return the AWMF-0108 phase settings
  """

  def __init__(self, theta, phi, waveLength, beamStrength):
    """Inits the object with polar coordinate input 
    theta           polar angle offset in degrees
    phi             azimuth angle offset in degrees
    waveLength      ...
    beamStrength    useless for now"""

    self.theta = radians(theta) #math module functions use radians
    self.phi = radians(phi)
    self.beamStrength = beamStrength
    self.waveLength = waveLength

    #AWMF-0108 constants
    self.phaseControlRange = 32
    self.gainControlRange = 32

    self.phaseControlMax = 2 * pi; #radians
    self.gainControlMax = 1; #??? check units on this


  def maxArrayFactor(self):
    """Warning, brute force incoming O(32^4*2^2)

    given a theta and phi angle, return the I and d arrays that produce
    the maximum beam in that direction

    return  array containing the phase offsets for each antenna [[NW, NE], [SW, SE]]
            maximum"""

    #I is just going to be uniformly illuminated
    I = [[1,1], [1,1]]

    #Tests every possible phase configuration possible and only keep the best one
    maxAF = 0
    maxAF_d = []
    for w in range(0, self.phaseControlRange):
      for x in range(0, self.phaseControlRange):
        for y in range(0, self.phaseControlRange):
          for z in range(0, self.phaseControlRange):
            d = [[w, x], [y,z]]
            #scales every value of d to be in proper phase units
            map(lambda x: map(lambda y: y*self.phaseControlMax/self.phaseControlRange, x), d)

            testAF = self._ArrayFactorPlanar(self.theta, self.phi, I, d, self.waveLength)
            if abs(testAF) > abs(maxAF):
              maxAF = testAF
              maxAF_d = d

    return maxAF_d, abs(maxAF)

  def _ArrayFactorPlanar(self, theta, phi, I, d, waveLength):
    """ private: calculate the strength of a configuratio at angle theta/phi
    on a square plane antenna array.
    I:  2D array of amplitudes of each element in square array
    d:  2D array of phases of each element in square array

    return: scalar ArrayFactor (not normalized)"""

    dist = 1 #placeholder -- distance between adjacent elements
    k = 2 * pi / waveLength # k = wave number
    
    cumulativeAF = 0
    for n in range(0, 2):
      for m in range(0,2):
        #intermediate variables for whats about to come
        n_factor = k*dist*n*sin(theta)*cos(phi)
        m_factor = k*dist*m*sin(theta)*sin(phi)

        #exponential term to calculate AF
        cumulativeAF += I[n][m] * exp(1j *(d[n][m] + n_factor + m_factor))

    return cumulativeAF

def main():
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
  main()
  t2 = time()
  tt = t2 - t1
  print "Total time elapsed: " + tt.__str__() + "s"
