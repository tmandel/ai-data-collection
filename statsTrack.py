#https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford's_online_algorithm
import math

class StatsTracker:

    def __init__(self):
        self.existingAggregate = (0,0,0)

    def update(self, newValue):
        (count, mean, M2) = self.existingAggregate
        count += 1
        delta = newValue - mean
        mean += delta / count
        delta2 = newValue - mean
        M2 += delta * delta2

        self.existingAggregate =  (count, mean, M2)


    def getMean(self):
        (count, mean, M2) = self.existingAggregate
        return mean

    def getCI(self):
        (count, mean, M2) = self.existingAggregate
        variance = M2 / count
        stddev = math.sqrt(variance)
        se = stddev / math.sqrt(count)
        return 1.96*se
