
import numpy
from scipy.stats import norm

# Simple class for a Normal (Gaussian) Distribution
#
# Parameters: mean (mu) and standard deviation (sigma)
class NormalDistribution(object):
    def __init__(self, mean, stdDev):
        self.mean = mean
        self.stdDev = stdDev

    #Draws a single sample from the distribution
    def sample(self):
        samples = numpy.random.normal(self.mean, self.stdDev, 1)
        return samples[0]

    #gets the standard deviation
    def getStdDev(self):
       return self.stdDev

    #gets the mean
    def getMean(self):
       return self.mean


# Simple class for a Normal (Gaussian) Distribution
# which is clamped to some given range
#
# Parameters: mean (mu), standard deviation (sigma), minVal, maxVal
class ClampedGaussianDistribution(object):
    def __init__(self, mean, stdDev, minVal, maxVal):
        self.mean = mean
        self.stdDev = stdDev
        self.minVal = minVal
        self.maxVal = maxVal

    #Draws a single sample from the distribution
    def sample(self):
        samples = numpy.random.normal(self.mean, self.stdDev, 1)
        sample = samples[0]
        if sample < self.minVal:
            return self.minVal
        if sample > self.maxVal:
            return self.maxVal
        return sample

    #gets the base standard deviation (may not be actual due to clamping)
    def getStdDev(self):
       return self.stdDev

    # doesnt actually give the real mean due to clamping
    def getMean(self):
       return self.stdDev


# Simple class for a Beta Distribution
# Parameters: alpha and beta
class BetaDistribution(object):
    def __init__(self, alpha, beta):
        self.alpha = alpha
        self.beta = beta

    #Draws a single sample from the distribution
    def sample(self):
        samples = numpy.random.beta(self.alpha, self.beta, 1)
        return samples[0]

    #get alpha parameter
    def getAlpha(self):
       return self.alpha

    #gets beta parameter
    def getBeta(self):
       return self.beta
       
       
       
# Models a Pareto Distribution.
# See https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.random.pareto.html#numpy.random.pareto
# See https://en.wikipedia.org/wiki/Pareto_distribution     
class ParetoDistribution(object):
    def __init__(self, shape, scale):
        self.shape = shape
        self.scale = scale

    #Draws a single sample from the distribution
    def sample(self):
        samples = (numpy.random.pareto(self.shape, 1) + 1) * self.scale
        return samples[0]

    #get shape parameter
    def getShape(self):
       return self.shape

    #get scale parameter
    def getScale(self):
       return self.scale


       
       
       
       
       
