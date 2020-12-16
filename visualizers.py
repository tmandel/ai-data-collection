import random
import math
import environments as envs
import distributions as dists
import utilities as util

# Interface (abstract) for vizualizer objects.
class Visualizer(object):

    # Re-initilializes with a given MIEnvironment
    # Returns True if initialization was successful, False otherwise
    def initWithEnvironment(self,env):
        pass

    # Processes a sample from environment.
    # Takes in a single xValue(int), and a single yValue(double)
    def processSample(self, xValue, yValue):
        pass

    # Returns a tuple of functions(lofunc,func, hifunc)
    # All functions should be dictionaries (x maps to y)
    # "function" is the measured response function.
    # It is guaranteed that lowfunc(x) <= func(x) <= hifunc(x).
    # Returned tuple wil be used for visualizations.
    def generateVisualization(self):
        pass

class BasicVisualizer(Visualizer):

    def __init__(self, delta):
        #Delta represents the chance of the true value falling outside the confidence intervals.
        #Example: 0.05 = 95% confidence interval.
        self.delta = delta

    # Re-initilializes with a given MIEnvironment
    # Returns True if initialization was successful, False otherwise
    def initWithEnvironment(self, env):
        self.env = env
        self.samples = [] 
        for i in self.env.getXRange():
            self.samples.append([])
        return True

    # Processes a sample from environment.
    # Takes in a single xValue(int), and a single yValue(double)
    def processSample(self, xValue, yValue):
        self.samples[xValue].append(yValue)

    # Returns a tuple of functions(lofunc,func, hifunc)
    # All functions should be dictionaries (x maps to y)
    # "function" is the measured response function.
    # It is guaranteed that lowfunc(x) <= func(x) <= hifunc(x).
    # Returned tuple wil be used for visualizations.
    def generateVisualization(self):  
        func = {} #func is just the average
        lowFunc = {}
        highFunc = {}
        for i in self.env.getXRange():
            if len(self.samples[i]) == 0:
                func[i] = (self.env.getMaxSample() + self.env.getMinSample())/2 
            else:
                func[i] = sum(self.samples[i])/len(self.samples[i])                
                
            confIntv = util.getCI(self.samples[i], self.delta)
            if confIntv is None:
                confIntv = 1    
            confIntv *=(self.env.getMaxSample() - self.env.getMinSample())
                
            lowFunc[i]=(util.clampY(self.env, func[i] - confIntv))
            highFunc[i]=(util.clampY(self.env, func[i] + confIntv))
        return (lowFunc, func, highFunc)
