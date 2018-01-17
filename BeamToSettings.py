#-------------------------------------------------------------------------------
# Name:        Beam Definition
# Purpose:     Convert from polar coordinates
#
# Author:      Grayson Colwell
#
# Created:     12/12/2017
# Copyright:   (c) Anokiwave Capstone Team 2017
# Licence:     <Memes>
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


  def maxArrayFactor(self):
    """WArning, brute force incoming O(32^4*2^2)

    given a theta and phi angle, return the I and d arrays that produce
    the maximum beam in that direction

    return  array containing the phase offsets for each antenna [[NW, NE], [SW, SE]]"""

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
            testAF = self._ArrayFactorPlanar(self.theta, self.phi, I, d, self.waveLength)
            if abs(testAF) > abs(maxAF):
              maxAF = testAF
              maxAF_d = d

    return d

  def _ArrayFactorPlanar(self, theta, phi, I, d, waveLength):
    """ private: calculate the strength of a configuratio at angle theta/phi
    I:  array of amplitudes of each element
    d:  array of phases of each element

    return: scalar ArrayFactor (not normalized)"""

    dist = 1 #placeholder -- distance between adjacent elements
    k = 2 * pi / waveLength # k = wave number

    cumulativeAF = 0
    for n in range(0,1):
      for m in range(0,1):
        #intermediate variables for whats about to come
        n_factor = k*dist*n*sin(theta)*cos(phi)
        m_factor = k*dist*m*sin(theta)*sin(phi)

        #exponential term to calculate AF
        cumulativeAF += I[n][m] * exp(d[n][m] + n_factor + m_factor)

    return cumulativeAF

