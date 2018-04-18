#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        Beam Definition
# Purpose:     Convert from polar coordinates to awmf-0108 settings
#
# Author:      Andy MacGregor 
#
# Created:     1/12/2017
# Copyright:   (c) Anokiwave Capstone Team 2017
# Licence:     tbd by Anokiwave 
#-------------------------------------------------------------------------------

from math import sin, cos, atan, pow, e, pi, radians, trunc, degrees
from cmath import exp
import yaml
import copy

#quadrant indexes
NW = "NW"
SW = "SW"
SE = "SE"
NE = "NE"

class BeamDefinition:
  """ Calculates AWMF phase settings from beam definition
  
  Give it spherical coordinates, and it can return the AWMF-0108 phase settings
  """
  #speed of light
  C = 299792458

  


  def __init__(self, theta, phi, waveLength, phaseCalFile="phaseCal.yaml", beamStrength=None):
    """Inits the object with polar coordinate input 
    theta           polar angle offset in degrees
      0 degrees = broadside beam
    phi             azimuth angle offset in degrees
      0 degrees = North
    waveLength      wavelength *in meters*
    phaseCalFile    yaml file for calibrating the phase offset 
    beamStrength    useless for now. leave blank.

    A = BeamDefinition(theta, phi, wavelength) 

    A.maxArrayFactor()
      [[x, x],[x, x]], maxAf """

    self.theta = radians(theta) #internal angles are all radians
    self.phi = radians(phi)
    self.beamStrength = beamStrength
    self.waveLength = waveLength

    #AWMF-0108 constants
    self.phaseControlRange = 32
    self.phaseControlMax = 2 * pi; #radians
    self.gainControlRange = 32
    self.gainControlStep = 1 #dB of attenuation per A value
    self.gainControlMaxRx = 28 #dB
    self.gainControlMaxTx = 26 #dB

    #default antenna parameters
    #antenna grid - says where each radiating element sits
    #            ex. 2x2:
    #            [ [NW , NE],
    #              [SW , SE]]
    #
    #            ex. 4x1:
    #            [ [NE, NW, SE, SW]]
    self.antennaGrid = [[NW, NE], [SW, SE]] 
    #self.antennaGrid = [[NE, NW, SE, SW]] # (x_dimension, y_dimension)

    self.antennaInvert = [[True, False], [True, False]]
    #self.antennaInvert = [[True, False, True, False]]
    self.antennaSpacing = 5.4 * pow(10,-3) #space between the center of antennas (meters)

    #Calculated awmf0108 settings... calculate when needed
    self.phaseSettings = []
    self.phaseSettingsRaw = []
    self.gainSettings = []

    #Calibration settings for this particular loadout. Fill now
    self.phaseCal = self.loadPhaseCal(phaseCalFile)


  def getPhaseSettings(self):
    """
      returns:  array containing the phase offset for each antenna 
                to point at the specified theta/phi direction in awmf-0108 settings
                
                returns a 1x4 array with settings for - NE-SE-SW-NW


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
    ns_angle = atan( cos(p) * sin(t) / cos(t) )

    d = self.antennaSpacing

    ##calculate offsets between elements    
    ew_phaseOffset = -k * d * sin(ew_angle)
    ns_phaseOffset = -k * d * sin(ns_angle)

    ##Calculate offsets for each element
    #inifialize offset list with zeros
    offsets = [ [0 for x in range(len(self.antennaGrid[0]))] for y in range(len(self.antennaGrid))]
    for i in range(0, len(self.antennaGrid)): # i = numrows of antenna
      # add ns offset between rows
      if i == 0:
        offsets[0][0] = 0
      else:
        offsets[i][0] = offsets[i-1][0] + ns_phaseOffset
      
      # add ew offset between columns
      for j in range(1, len(self.antennaGrid[0])): # j = numcols = x dimension
        offsets[i][j] = offsets[i][j - 1] + ew_phaseOffset

    #will be used in generateAllAF
    self.phaseSettingsRaw = copy.deepcopy(offsets)

    #add phase flip
    for i in range(0, len(self.antennaGrid)):
      for j in range(0, len(self.antennaGrid[0])):
        if self.antennaInvert[i][j]:
          offsets[i][j] += pi

    #Changes offsets from a 2d array to a flat dictionary indexed by quadrant.
    #I'm sorry for writing it this way
      #how it works - 1 flatten antennaGrid and offsets with that list comprehension
      #               2 zip the flattened list into paired tuples
      #               3 make a dictionary from the tuples & call it d_offsets
    d_offsets = dict(zip( [j for i in self.antennaGrid for j in i], [j for i in offsets for j in i]))

    #convert the offset dictionary to settings from phase angle
    s_offsets = {key: self._radiansToAwmf0108(val) for key, val in d_offsets.items()}

    #apply phase calibration and convert to a plain array
    n_offsets = [ self._applyCalibration(x, s_offsets[x], self.phaseCal) for x in [NE, SE, SW, NW]]

    self.phaseSettings = n_offsets
    
    return n_offsets

  def getRawPhaseSettings(self):
    """
      Gets an array of phase settings as a 2D array - same mapping as self.antennaGrid, in radians
      Removes phase inverts to specified patches.

      Maps the information stored in self.phaseSettings to locations specified
      by self.antennaGrid
    """
    
    #make sure its calc'd 
    if len(self.phaseSettingsRaw) == 0:
      self.getPhaseSettings()

    return self.phaseSettingsRaw

  def getGainSettings(self):
    """ 
      Return gain settings for this configuration.
      As long as we're using uniform illumination, set it all to 1
    """
    if len(self.gainSettings) > 0 :
      return self.gainSettings

    xdim = len(self.antennaGrid)
    ydim = len(self.antennaGrid[0])
    self.gainSettings = [[1 for x in range(xdim)] for y in range(ydim)]

    return self.gainSettings


  def setAntenna(self, grid, invertPattern, spacing):
    """ 
      Replaces the default antenna parameters with ones specified by the user.
    """
    self.antennaGrid = grid 
    self.antennaSpacing  = spacing
    self.antennaInvert = invertPattern

    #force recalulation of gain and phase settings
    self.phaseSettings = []
    self.gainSettings = []
    return


  def generateAllAF(self, n_theta=30, n_phi=30, normalized=True, absAf=True, backLobes=False):
    """
      n_theta: resolution of display in points 

      returns:  a ***sorted*** list of tuples to graph (theta, phi,  AF) 
          with units (radians, radians, unitless)
        sorted by phi first then by theta, from least to greatest

        AF is normalized to 1 by default
        Only uses the magnitude component of the Af by default
        backLobes -- set true if you want to see the pattern on the back of the antenna
        
    """
    #iterate from theta = 0 to 180 and phi = 0 to 360 in increments of d_theta and d_phi
    t = 0
    p = 0
    t_max = 180 if backLobes else 90
    p_max = 360

    p_d = p_max / n_phi
    t_d = t_max / n_theta

    points = []
    
    af_max = -1

    while t < t_max :
      while p < p_max :
        # calculate the Antenna Factor for this angle at these settings and add it
        # to the list
        a = self._calculateArrayFactor(radians(t), radians(p), self.getGainSettings(), self.getRawPhaseSettings(), self.waveLength);

        if absAf:
          a = abs(a)

        points.append( (t, p, a) )

        if abs(a) > abs(af_max):
          af_max = a

        p = p + p_d
      p = 0
      t = t + t_d
    
    print(self.phaseSettingsRaw)

    if normalized:
      return [(t, p, a/abs(af_max)) for (t, p, a) in points] #divide all afs by af_max
    else:
      return points

  #########Helper-funciton-land

  def _calculateArrayFactor(self, theta, phi, I, d, waveLength):
    """ 
    private: calculate the strength of a configuratio at angle theta/phi
    on a square plane antenna array.
    
    I:  2D array of amplitudes of each element in square array (scale from 0 to 1.0)
    d:  2D array of phases of each element in square array (radians)
      **Must have dimensions self.antennaGrid
    
    return: scalar ArrayFactor (not normalized)
    """

    dist = self.antennaSpacing 
    k = 2 * pi / waveLength # k = wave numer
    
    cumulativeAF = 0
    for n in range(0, len(self.antennaGrid)):
      for m in range(0, len(self.antennaGrid[0])):
        #exponential term to calculate AF
        costerm = k*dist*n*sin(theta)*cos(phi)
        sinterm = k*dist*m*sin(theta)*sin(phi)
        cumulativeAF += I[n][m] * exp(1j *(d[n][m] + costerm + sinterm))

    return cumulativeAF


  def _applyCalibration(self, quadrant, setting, calMap):
    """ 
    Applies a calibration to a single setting _if the calibration map exists_
    and returns the result
    """
    if calMap: #only if a structure was loaded
      #setting probably won't appear in the calMap. Find the nearest thing that does
      closestSetting = min(calMap[quadrant].keys(), key=lambda x:abs(x - setting))

      #Only talk about the calibration if its being used
      if calMap[quadrant][closestSetting] != 0:
        if closestSetting != setting:
          print("Calibration -- Using: " + closestSetting.__str__() + " instead of " + setting.__str__())
        print("Calibration -- Applying: " + calMap[quadrant][closestSetting].__str__() + " to " + quadrant)
      
      return (setting - calMap[quadrant][closestSetting]) % 32
    else:
      return setting 


  def _radiansToAwmf0108(self, rads):
    """
      rads: angle in radians to convert
      return: phase setting in awmf-0108 format
    """
    interval = self.phaseControlMax / self.phaseControlRange
    
    #fix to be in range between 0 and 2pi radians
    fixed = rads % (2*pi)

    val = trunc(self._roundToNearest(fixed, interval) / interval);

    #fix to prevent from returning 32 instead of 0
    if val == self.phaseControlRange:
      val = 0

    return val

  def _Awmf0108ToRadians(self, awmf):
    """
      rads: angle in radians to convert
      return: phase setting in awmf-0108 format
    """
    interval = self.phaseControlMax / self.phaseControlRange
    
    #fix to be in range between 0 and 2pi radians
    fixed = rads % (2*pi)

    val = trunc(self._roundToNearest(fixed, interval) / interval);

    #fix to prevent from returning 32 instead of 0
    if val == self.phaseControlRange:
      val = 0

    return val

  def _roundToNearest(self, x, multiple):
    """
      round x to the nearest multiple of _multiple_
      credit to stackOverflow
    """
    return multiple * round( float(x) / multiple)


  def loadPhaseCal(self, phaseCalFile):
    """ 
      Load a phase calibration yaml file into a data structure 
      return the data structure

      2-level dictionary structure:
        cal[X][p] = settingoffset error for quadrant X at phase setting p

      Cal file is expected as follows --
      NW: {
          0: 3
          1: -2
          ...
          }
      QUADRANT: {
        PHASE_SETTING: [Measurement - Setting]
      }

    #All units are in settings.
    """
    #load the dictionary raw
    try:
      with open(phaseCalFile, "r") as stream:
        dataMap = yaml.safe_load(stream) #just assume its correct
    except IOError: #Python2 doesn't have FileNotFoundError
      print("No phase calibration file found.")
      return None

    return dataMap


################################################################################
##Test 


def unCheckedTestCase(t, p, w, i):
  b1 = BeamDefinition(t, p, w, phaseCalFile="0phaseCal.yaml") 
  d1 = b1.getPhaseSettings()
  print ("BeamDefinition(" + t.__str__() + ", " \
   + p.__str__() + ", " + w.__str__() + ", " + i.__str__() + ") ")
  print( "2x2\t" + d1.__str__())
  
  b1.setAntenna( [[NE, NW, SE, SW]], [[ True, False, True, False]],5.4 * pow(10,-3))
  d1 = b1.getPhaseSettings()
  print("1x4\t" + d1.__str__() + "\n")


def testBeamDefinition():
  """Test harness for this module """
  #Does some test calculations to make sure the module functions
  f = 28 * pow(10,9) #29GHz
  c = 3 * pow(10, 8)
  w = c/f 

  #----------------------------------
  ## Basic tests to see different outputs
  unCheckedTestCase(30, 90, w, 1)
  unCheckedTestCase(15, 90, w, 1)
  
  unCheckedTestCase(-30, -90, w, 1)
  unCheckedTestCase(-30, -90, w, 1)

  unCheckedTestCase(15, 0, w, 1)
  unCheckedTestCase(15, 180, w, 1)
  #--------------------------------------

  #--------------------------------------
  ##Tests to run in the anechoic chamber:
  print("Anechoic chamber candidates:\n\n\n")
  unCheckedTestCase(0, 90, w, 1) #phi=90 = inline with the 1x4 array

  unCheckedTestCase(30, 90, w, 1) 
  unCheckedTestCase(20, 90, w, 1) 
  unCheckedTestCase(10, 90, w, 1)
  unCheckedTestCase(-10, 90, w, 1)
  unCheckedTestCase(-20, 90, w, 1)
  unCheckedTestCase(-30, 90, w, 1) 

  ##Test phaseCal loading
  b1 = BeamDefinition(0, 0, w, phaseCalFile="testPhaseCal.yaml")
  d1 = b1.getPhaseSettings()
  print( "Funny cal: \t" + d1.__str__())
  


if __name__ == '__main__':
  from time import time
  t1 = time()
  testBeamDefinition()
  t2 = time()
  tt = t2 - t1
  print("Total time elapsed: " + tt.__str__() + "s")

1