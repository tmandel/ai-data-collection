import random
import distributions as dist
import sys
import json
# Abstract class.
# A fully-defined Mixed Initiative Sampling Environment
class MIEnvironment(object):

    #Re-initializes the environment from scratch
    #Returns True if reset successful, False otherwise
    def reset(self):
        pass

    # Takes in a xValue(int)
    # yValues are:
    # Guranteed to be between minSample and maxSample
    # Guranteed to be sampled from the distribution @ the passed in xValue.
    # Returns a y value and list storing a tuple of x and y values.
    def sample(self,xValue):
        pass

    # Generates true function, (true mean yValues for all xValues).
    def generateTrueFunction(self):
        pass
    
    def getXRange(self):
        pass

    def getMinSample(self):
        pass
    
    def getMaxSample(self):
        pass   

#Interface provided to the learner for getting the known aspects of the environment
#Takes in a fully defined environment and "hides" unknown info
class MIEnvironmentInfo(object):
    def  __init__(self, env):
        self.xRange = env.getXRange()
        self.minSample = env.getMinSample()
        self.sample = env.getMaxSample()

    def getXRange(self):
        return self.xRange

    def getMinSample(self):
        return self.minSample

    def getMaxSample(self):
        return self.sample


class DataDrivenEnv(MIEnvironment):
    def __init__(self, jsonFName):
        f = open(jsonFName, 'r', encoding='utf-8')
        dictionary = json.load(f)
        f.close()
        
        if len(dictionary['xVals']) != len(dictionary['yVals']):
            print('xVals and yVals are different lengths in ' + dictionary['title'] + \
                  ' please fix this before continuing.')
            sys.exit(1)

        self.title = dictionary['title']
        self.description = dictionary['description']
        self.xRange = range(len(dictionary['xVals']))
        self.xVals = dictionary['xVals']
        self.yVals = dictionary['yVals']
        self.xlabel = dictionary['xlabel']
        self.ylabel = dictionary['ylabel']
        allSamples = dictionary['All_sample']

        overallMax=None
        overallMin=None
        for key in allSamples:
            minValue = min(allSamples[key])
            maxValue = max(allSamples[key])
            if overallMax is None or maxValue>overallMax:
                overallMax = maxValue
            if overallMin is None or minValue<overallMin:
                overallMin = minValue
        self.miny = overallMin
        self.maxy = overallMax
        
        self.allSamplesList = []
        for i in range(len(self.xVals)):
            key = self.xVals[i]
            y = self.yVals[i]
            self.allSamplesList.append(allSamples[key])
            average = sum(allSamples[key])/len(allSamples[key])
            difference = average - y
            absDiff = abs(difference)
            if absDiff > 0.0000001:
                print('Samples in json file do not match. Cannot preceed')
                sys.exit(1)

    #Re-initializes the environment from scratch
    #Returns True if reset successful, False otherwise
    def reset(self):
        return True

    # Takes in a xValue(int)
    # yValues are:
    # Guaranteed to be between minSample and maxSample
    # Guaranteed to be sampled from the distribution @ the passed in xValue.
    # Returns a y value and list storing a tuple of x and y values.
    def sample(self,xValue):
        y = random.choice(self.allSamplesList[xValue])
        return (y, [(xValue,y)])

    # Generates true function, (true mean yValues for all xValues).
    def generateTrueFunction(self):
        trueFunction = {}
        for x in self.xRange:
            trueFunction[x] = self.yVals[x]
        return trueFunction


    def getXRange(self):
        return self.xRange


    def getMinSample(self):
        return self.miny

    
    def getMaxSample(self):
        return self.maxy
    
    
    
    
    
