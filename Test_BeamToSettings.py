#!/usr/bin/python

from BeamToSettings import BeamDefinition
from math import pow

#Does some test calculations to make sure the module functions
w = 28 * pow(10,9) #29GHz

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

#with 0 and 0 you'd expect even phase offset
bUniform = BeamDefinition(0, 0, w, 1)
dU = bUniform.maxArrayFactor()
print "BeamDefinition(0, 0, w, 1)"
print dU.__str__()  + "\n"

assert dU[0][0] == dU[0][1] == dU[1][0] == dU[1][1]

#TODO Create some test cases with other values that you can assert
