import math
import Dice

EPSILON = 0.000001

def find_median(rolls):
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

def convert_to_binary(rolls, median):
    ms = []
    for roll in rolls:
        if roll <= median:
            ms.append(0)
        else:
            ms.append(1)
    return ms

def count_zeros(rolls):
    count = 0
    for roll in rolls:
        if roll == 0:
            count += 1
    return count

def count_runs(rolls):
    prev = None
    count = 0
    for roll in rolls:
        if roll != prev:
            count += 1
        prev = roll
    return count

def count_positive_diffs(rolls):
    prev = 7
    count = 0
    for roll in rolls:
        if roll > prev:
            count += 1
        prev = roll
    return count

def count_non_zero_diffs(rolls):
    prev = None
    count = 0
    for roll in rolls:
        if prev != None and roll != prev:
            count += 1
        prev = roll
    return count

def trim_zero_runs(rolls):
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


def fail_if_abnormal(val, mean, var):
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


class TestDice(object):
    def setup_method(self, method):
        self.trials = 600
        self.dice = Dice.Dice()
        self.rolls = []
        self.bins = {}
        for unused in xrange(self.trials):
            num = self.dice.roll()[0]
            self.rolls.append(num)
            self.bins[num] = self.bins.get(num, 0) + 1

    def test_find_median(self):
        assert find_median([]) == None
        assert find_median([0]) == 0
        assert find_median([-2, 0, 25]) == 0
        assert find_median([25, -2, 0]) == 0
        assert abs(find_median([2, 0.15, 3, 4329473]) - 2.5) < EPSILON

    def test_convert_to_binary(self):
        assert (convert_to_binary([-11111, 0.1, 2, 3, 4, 23947], 2.5) ==
          [0, 0, 0, 1, 1, 1])

    def test_count_runs(self):
        assert count_runs([1, 2, 2, 2, 3, 2, 1, 6, 6, 5, 5, 1]) == 8

    def test_count_positive_diffs(self):
        assert count_positive_diffs([]) == 0
        assert count_positive_diffs([3, 3, 4, 2, 5, 3, 4, 2, 6, 1]) == 4

    def test_count_non_zero_diffs(self):
        assert count_non_zero_diffs([]) == 0
        assert count_non_zero_diffs([3, 3, 4, 2, 5, 3, 4, 2, 6, 1]) == 8

    def test_trim_zero_runs(self):
        assert trim_zero_runs([]) == []
        assert trim_zero_runs([3, 3, 4, 2, 5, 3, 4, 2, 6, 1]) == \
                              [3, 4, 2, 5, 3, 4, 2, 6, 1]

    def test_M(self):
        """Recode each sample as 0 if <= sample median, 1 if > sample median
        M is number of runs of consecutive 0s and 1s.
        r is number of 0s.
        null hypothesis, mean and variance of M in n observations are about
        mean_M = 2*r*(n-r)/n + 1
        variance_M = 2*r*(n-r)*(2*r*(n-r)-n)/(n*n*(n-1))
        for large samples Z_M = (M - mean_M) / standard_dev_M is standard 
        normal
        prob (M <= val) = Pr((M-meanM)/sd_M = Pr(Z)
        """
        median = find_median(self.rolls)
        ms = convert_to_binary(self.rolls, median)
        r = count_zeros(ms)
        M = count_runs(ms)
        n = self.trials
        mean_M = 2. * r * (n - r) / n + 1.
        var_M = (((2. * r) * (n - r) / n ** 2 * ((2. * r) * (n - r) - n)) /
          (n - 1.))
        print "M test: r =", r, "M = ", M, "mean = ", mean_M, "var =", var_M
        fail_if_abnormal(M, mean_M, var_M)

    def test_sign(self):
        """P is number of positive signs among x2-x1, x3-x2, etc. (not zeros)
        If M non-zero values of xi - x(i-1), mean_P is m/2, variance_P is M/12
        """
        P = count_positive_diffs(self.rolls)
        M = count_non_zero_diffs(self.rolls)
        mean_P = M / 2.
        var_P = M / 12.
        print "Sign test: P =", P, "M = ", M, "mean = ", mean_P, "var =", var_P
        fail_if_abnormal(P, mean_P, var_P)

    def test_runs(self):
        trimmed = trim_zero_runs(self.rolls)
        m = len(trimmed)
        pos = count_positive_diffs(trimmed)
        neg = m - pos
        R = 0. + pos
        mean_R = 1. + (2 * pos * neg) / (pos + neg)
        var_R = ((( 2. * pos * neg) * (2. * pos * neg - pos - neg)) /
                ((pos + neg) * (pos + neg) * (pos + neg - 1)))
        print "Runs test: R =", R, "m = ", m, "mean = ", mean_R, "var =", var_R
        fail_if_abnormal(R, mean_R, var_R)

    def test_mann_kendall(self):
        S = 0
        n = len(self.rolls)
        for i in xrange(1, n):
            for j in xrange(i):
                val = sign(self.rolls[i] - self.rolls[j])
                S += val
        mean_S = 0.
        var_S = (n / 18.) * (n - 1.) * (2. * n + 5.)
        print "Mann-Kendall test: S =", S, "mean = ", mean_S, "var =", var_S
        fail_if_abnormal(S, mean_S, var_S)

    def test_shuffle(self):
        s = set()
        lst = range(10)
        s.add(tuple(lst))
        num_shuffles = 100
        for unused in range(num_shuffles):
            self.dice.shuffle(lst)
            s.add(tuple(lst))
        # We are highly unlikely to get a duplicate.  Though it's possible...
        assert len(s) == num_shuffles + 1
