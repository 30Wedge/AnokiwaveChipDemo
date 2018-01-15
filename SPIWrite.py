#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Grayson Colwell
#
# Created:     12/12/2017
# Copyright:   (c) Anokiwave Capstone Team 2017
# Licence:     <Memes>
#-------------------------------------------------------------------------------

from ni8452io import SPI


testSPI = SPI()

fret = testSPI.ioOpen
print 'ioOpen():  \t{0}'.format(fret)
if fret != 0:
    exit(0)

fRet = testSPI.ioSetConfig(spiClk=1000000)
print 'ioSetConfig():\t{0}'.format(fret)
if fret != 0:
    exit(0)

fret = testSPI.ioInit
print 'ioInit():  \t{0}'.format(fret)
if fret != 0:
    exit(0)

if fret == 0:
    #begin test to send bits from the NI8452 to Interposer board
    wArr = range(0, 27)
    rData = testSPI.ioWriteSPI(wArr)
    print rData





