import random
import math
import environments as envs
import distributions as dists
import visualizers as vis
import utilities as util
from cheater import Cheater
import sys
import json

# Interface (abstract) class for evaluator objects.
class Evaluator(object):
    # Re-initilializes with a given MIEnvironment
    # Returns True if initialization was successful, False otherwise
    def initWithEnvironment(self,env):
        pass

    # Processes a sample used to get a better estimate of the function.
    #
    def processEvalSample(self, xValue, yValue):
        pass

    # Processes a sample to evaluate how well the AI is directing samples.
    #
    def processAISample(self, xValue, yValue):
        pass

    def processEmpiricalKeypoints(self, currentKeypoints):
        pass
    
    # Keypoints should be generated by estimateFunction
    # Takes in current keypoints.
    # Keypoints are a list of tuples: [(x,y),(x,y),(x,y)...]
    def processKeypoints(self,currentKeypoints):
        pass

    # Returns the currents score based on the latest keypoints and history of processed samples
    def getCurrentScore(self):
        pass

    # Generates a statisically correct estimate of the response function from the processed samples.
    def estimateFunction(self):
        pass

    def getNonKeypointSamples(self):
        pass
    

class RegretEvaluator(Evaluator, Cheater):
    def __init__(self):         
        self.score = 0.0
        pass

    def initWithEnvironment(self, env):
        self.samples = [] 
        self.score = 0
        for i in env.getXRange(): #intentionally NOT self.env
            self.samples.append([])
        # altEnv exists to make env.getXRange() accessible, later.    
        self.altEnv = env
        self.empKeypoints = []
        return True

    def passTrueEnvironment(self, trueEnvironment):
        self.env = trueEnvironment
        pass

    def getScientistPreferredCILevel(self):
        return 0.1

    def processEvalSample(self, xValue, yValue):
        #Do nothing.
        return 

    def processAISample(self, xValue, yValue):
        self.lastXValue = xValue
        self.samples[xValue].append(yValue)

    def removeLastSample(self,xValue):
        self.samples[xValue].pop()

    def processEmpiricalKeypoints(self, currentKeypoints):
        self.empKeypoints = currentKeypoints
        self.empKeypointXs = [x for (x,y) in currentKeypoints]
        
    def processKeypoints(self, currentKeypoints):
        newEmpScore = util.getEvalScore(self.samples, currentKeypoints, self.getScientistPreferredCILevel())
        lastY = self.samples[self.lastXValue].pop()
        optX = util.chooseOptimalXValue(currentKeypoints, self.samples)
        self.samples[optX].append(1) # Exact Val doesn't matter
        
        newOptScore = util.getEvalScore(self.samples, currentKeypoints, self.getScientistPreferredCILevel())
        self.samples[optX].pop()
        self.samples[self.lastXValue].append(lastY)
         
        regret = (newOptScore - newEmpScore)
        if regret < - 0.000001:
            print("something's wrong with the score!")
            print("opt score diff is", (newOptScore - oldOptScore), "with", len(currentKeypoints), "keypoints:", [k[0] for k in currentKeypoints])
            print("emp score diff is", (newEmpScore - oldEmpScore), "with", len(self.empKeypoints), "keypoints", [k[0] for k in self.empKeypoints])
            sys.exit(1)
        self.score = regret
        self.trueKeypoints = [x for (x,y) in currentKeypoints]

        self.lastKeypoints = currentKeypoints

    def getCurrentScore(self):
        return self.score

    def getEmpAlgScore(self):
        return util.getEvalScore(self.samples, self.empKeypoints, self.getScientistPreferredCILevel())

    def getSampleCount(self):
        countDict = {}
        for x in self.altEnv.getXRange():
            countDict[x] = len(self.samples[x])
        return countDict

    def getNonKeypointSamples(self):
        total = 0
        for x in self.altEnv.getXRange():
            if x not in self.empKeypointXs:
                total += len(self.samples[x])
        return total

    def estimateFunction(self):
     
        func = self.env.generateTrueFunction()
        lowFunc = highFunc = func
       
        return (lowFunc,highFunc)

