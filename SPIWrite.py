#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        spiwrite
# Purpose:     Write commands to the awmf-0108 through the spi interposer
#
# Author:      Grayson Colwell
#              Andy MacGregor
#
# Created:     12/12/2017
# Copyright:   (c) Anokiwave Capstone Team 2017
# Licence:     <Memes>
#-------------------------------------------------------------------------------

from ni8452io import SPI
#dll name is Ni845x.dll

#enumerate TXMODE, RXMODE, RX_11, SB
SB_MODE = 0
TX_MODE = 1
RX_MODE = 2
RX_11_MODE = 3
 
class AwmfCommander:
  """
  Sends commands to the awmf through the SPI interposer 
    using a system of different kites and drums

  usage:

  AwmfCommander.initSpi()
  AwmfCommander.setBeam(....)
  """

  testSPI = 0
  @classmethod
  def initSpi(cls):
    """ 
    opens the connection to the SPI bus and sets the clock
    """
    #open spi
    print("Starting init")

    cls.testSPI = SPI()
    fret = cls.testSPI.ioOpen()
    print 'ioOpen():  \t{0}'.format(fret)
    if fret != 0:
      exit(1) #TODO throw error instead of killing everything

    #set clock rate
    fRet = cls.testSPI.ioSetConfig(spiClk=1000000)
    print 'ioSetConfig():\t{0}'.format(fret)
    if fret != 0:
      exit(1)

    fret = cls.testSPI.ioInit()
    print 'ioInit():  \t{0}'.format(fret)
    if fret != 0:
      exit(1)

    print("Initialize Successfully")

  @classmethod
  def setBeam(cls, mode, NE_phase, SE_phase, SW_phase, NW_phase,
                    NE_amp, SE_amp, SW_amp, NW_amp):
    """
    Writes settings to the awmf for normal operation (no FBS)

    input is cast to byte arrays of the proper size. Pass in numbers for input

    bit:    name              write-value
    1-10    Control word      0
    
    10-14   NE RX phase       parameter value (LSB first)
    15-19   NE RX amp
    
    20-24   NE TX phase
    25-29   NE TX amp

    30-34   SE RX phase
    35-39   SE RX amp

    40-44   SE TX phase
    45-49   SE TX amp

    50-54   SW RX phase
    55-59   SW RX amp

    60-64   SW TX phase
    65-69   SW TX amp

    70-74   NW RX phase
    75-79   NW RX amp
    
    80-84   NW TX phase
    85-89   NW TX amp

    90-93   TX TVGA           ???
    94-97   RX TVGA           ???
    98      DIS_Telemetry     0
    99      x                 0 (always)
    """
    dataIn5Bits = []
    
    if(mode == RX_MODE):
      dataIn5Bits = [0, 0,
                   NE_phase, NE_amp,
                   0, 0,
                   SE_phase, SE_amp,
                   0, 0,
                   SW_phase, SW_amp,
                   0, 0,
                   NW_phase, NW_amp,
                   0, 0,
                   0, 0]
    elif(mode == TX_MODE):
      dataIn5Bits = [0, 0,
                   0, 0,
                   NE_phase, NE_amp,
                   0, 0,
                   SE_phase, SE_amp,
                   0, 0,
                   SW_phase, SW_amp,
                   0, 0,
                   NW_phase, NW_amp,
                   0, 0]
    #TODO toggle Tx_enable and rx_enable pins
    else:
      pass #TODO determine what to send in other cases
    
    wArr = self.__packValues(dataIn5Bits)
    rData = cls.testSPI.ioWriteSPI(wArr)

    print rData
    

  @staticmethod
  def __packValues(vals, width = 5):
    """
    takes a list of values (integers) and packs them as densely
    as possible into a  _little endian_ byte array

    assumes each element in vals is _width_ bits wide
    """
    byteArray = []
    cB = 0
    cBi = 0

    for val in vals:
      #for each meaningful bit in the current value
      for i in range(width):
        #set the next bit in the current working byte
            #whether or not the next bit in val is set
            #      |                   index of cB to set
        cB |= ( (val & (1 << i)) >>  i) << cBi
        cBi += 1

        if(cBi >= 8):
          byteArray.append(cB)
          cBi = 0
          cB = 0

    #append the remaining bits if there are any
    if(cBi != 0):
      byteArray.append(cB)
    return byteArray



# ------------------------------------------------------------------------------
# MAIN PROGRAM - TEST HARNESS
# ------------------------------------------------------------------------------
def main():
  #AwmfCommander.initSpi()

  ######__pack_values
  pv = AwmfCommander._AwmfCommander__packValues
  c1 = pv(range(10))
  assert(c1[0] == 0x20)
  assert(c1[1] == 0x88)
  assert(c1[2] == 0x41)

  c2 = pv([32], 5)
  assert(c2[0] == 0)



if __name__ == '__main__':
    main()





