#!/usr/bin/env python2.3

import unittest
import math
import Dice

EPSILON = 0.000001

def findMedian(rolls):
    """Find the median of a sequence of numbers."""
    if len(rolls) == 0:
        return None
    clone = list(rolls)
    clone.sort()
    midpoint = (len(clone) - 1) / 2.
    if abs(midpoint - round(midpoint)) <= EPSILON:
        return clone[int(round(midpoint))]
    else:
        return (clone[int(round(midpoint - 0.5))] +
                clone[int(round(midpoint + 0.5))]) / 2.

def convertToBinary(rolls, median):
    ms = []
    for roll in rolls:
        if roll <= median:
            ms.append(0)
        else:
            ms.append(1)
    return ms

def countZeros(rolls):
    count = 0
    for roll in rolls:
        if roll == 0:
            count += 1
    return count

def countRuns(rolls):
    prev = None
    count = 0
    for roll in rolls:
        if roll != prev:
            count += 1
        prev = roll
    return count

def failIfAbnormal(val, mean, var):
    """Fail if a result is outside the normal range."""
    # Avoid division by zero when we hit spot-on.
    if abs(var) < EPSILON:
        sd = 0
        z = 0
    else:
        sd = math.sqrt(abs(var))
        z = (val - mean) / sd
    if abs(z) > 3:
        assert False

class DiceTestCase(unittest.TestCase):
    def setUp(self):
        self.trials = 6000
        self.dice = Dice.Dice()
        self.rolls = []
        self.bins = {}
        for unused in xrange(self.trials):
            num = self.dice.roll()
            self.rolls.append(num)
            self.bins[num] = self.bins.get(num, 0) + 1

    def testFindMedian(self):
        assert findMedian([]) == None
        assert findMedian([0]) == 0
        assert findMedian([-2, 0, 25]) == 0
        assert findMedian([25, -2, 0]) == 0
        self.failUnlessAlmostEqual(findMedian([2, 0.15, 3, 4329473]), 2.5)
        self.failUnlessAlmostEqual(findMedian((2, 0.15, 3, 4329473)), 2.5)

    def testConvertToBinary(self):
        assert (convertToBinary([-11111, 0.1, 2, 3, 4, 23947], 2.5) ==
          [0, 0, 0, 1, 1, 1])

    def testCountRuns(self):
        assert countRuns([1, 2, 2, 2, 3, 2, 1, 6, 6, 5, 5, 1]) == 8

    def testM(self):
        """Recode each sample as 0 if <= sample median, 1 if > sample median
           M is number of runs of consecutive 0s and 1s.
           r is number of 0s.
           null hypothesis, mean and variance of M in n observations are about
           meanM = 2*r*(n-r)/n + 1
           varianceM = 2*r*(n-r)*(2*r*(n-r)-n)/(n*n*(n-1))
           for large samples Zm = (M - meanM) / standardDevM is standard normal
           prob (M <= val) = Pr((M-meanM)/sdM = Pr(Z)
        """
        median = findMedian(self.rolls)
        ms = convertToBinary(self.rolls, median)
        r = countZeros(ms)
        M = countRuns(ms)
        n = self.trials
        meanM = 2. * r * (n - r) / n + 1.
        varM = (((2. * r) * (n - r) / n ** 2 * ((2. * r) * (n - r) - n)) /
          (n - 1.))
        print "M test: r =", r, "M = ", M, "mean = ", meanM, "var =", varM
        failIfAbnormal(M, meanM, varM)



if __name__ == "__main__":
    unittest.main()
