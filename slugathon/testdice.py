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

def countPositiveDiffs(rolls):
    prev = 7
    count = 0
    for roll in rolls:
        if roll > prev:
            count += 1
        prev = roll
    return count

def countNonZeroDiffs(rolls):
    prev = None
    count = 0
    for roll in rolls:
        if prev != None and roll != prev:
            count += 1
        prev = roll
    return count

def trimZeroRuns(rolls):
    """Return the list with runs of identical rolls reduced to just one."""
    li = []
    prev = None
    for roll in rolls:
        if roll != prev:
            li.append(roll)
        prev = roll
    return li

def sign(num):
    """Return 1 if num is positive, 0 if zero, -1 if negative."""
    if num > 0:
        return 1
    elif num == 0:
        return 0
    else:
        return -1


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
        self.trials = 600
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

    def testCountPositiveDiffs(self):
        assert countPositiveDiffs([]) == 0
        assert countPositiveDiffs([3, 3, 4, 2, 5, 3, 4, 2, 6, 1]) == 4

    def testCountNonZeroDiffs(self):
        assert countNonZeroDiffs([]) == 0
        assert countNonZeroDiffs([3, 3, 4, 2, 5, 3, 4, 2, 6, 1]) == 8

    def testTrimZeroRuns(self):
        assert trimZeroRuns([]) == []
        assert trimZeroRuns([3, 3, 4, 2, 5, 3, 4, 2, 6, 1]) == \
                               [3, 4, 2, 5, 3, 4, 2, 6, 1]

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

    def testSign(self):
        """P is number of positive signs among x2-x1, x3-x2, etc. (not zeros)
           If m non-zero values of xi - x(i-1), meanP is m/2, varianceP is m/12
        """
        P = countPositiveDiffs(self.rolls)
        m = countNonZeroDiffs(self.rolls)
        meanP = m / 2.
        varP = m / 12.
        print "Sign test: P =", P, "m = ", m, "mean = ", meanP, "var =", varP
        failIfAbnormal(P, meanP, varP)

    def testRuns(self):
        trimmed = trimZeroRuns(self.rolls)
        m = len(trimmed)
        pos = countPositiveDiffs(trimmed)
        neg = m - pos
        R = 0. + pos
        meanR = 1. + (2 * pos * neg) / (pos + neg)
        varR = ((( 2. * pos * neg) * (2. * pos * neg - pos - neg)) /
                ((pos + neg) * (pos + neg) * (pos + neg - 1)))
        print "Runs test: R =", R, "m = ", m, "mean = ", meanR, "var =", varR
        failIfAbnormal(R, meanR, varR)

    def testMannKendall(self):
        S = 0
        n = len(self.rolls)
        for i in range(1, n):
            for j in range(i):
                val = sign(self.rolls[i] - self.rolls[j])
                S += val
        meanS = 0.
        varS = (n / 18.) * (n - 1.) * (2. * n + 5.)
        print "Mann-Kendall test: S =", S, "mean = ", meanS, "var =", varS
        failIfAbnormal(S, meanS, varS)


if __name__ == "__main__":
    unittest.main()
