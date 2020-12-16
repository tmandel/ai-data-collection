import random
import math
import environments as envs
import distributions as dists
import json

# Interface (abstract) for humanSampler objects.
class humanSampler(object):

    # Re-initilializes with a given MIEnvironment
    # Returns True if initialization was successful, False otherwise
    def initWithEnvironment(self,env):
        pass

    # This will be the first screen we show the user.
    # The screen will display hifunc and lofunc and will ask the user to select keypoints.
    # lofunc and hifunc should be dictionaries mapping x-values to y-values.
    # Returns keypoints.
    # The keypoints should be a list with tuples inside in the format [(x,y),(x,y),(x,y)]
    # Should not be stateful. (const function)
    def getUpdatedKeypoints(self, lofunc, hifunc):
        pass

    #Re-initializes the human sampler from scratch
    #Returns True if reset successful, False otherwise
    def tagOut(self):
        pass
    
    def buildTheoryFromInitialData(samples):
        pass
    

# Implements a dummy human that will select keypoints at critical points in the function.
#
# Idea: Keypoinmt when confident both low or both high
class CriticalPointsHuman(humanSampler):

    def __init__(self, tolerance, tolerDiff):
        self.tolerance = tolerance
        self.tolerDiff = tolerDiff
        pass

    def initWithEnvironment(self,env):
        self.env = env
        return True

    def getUpdatedKeypoints(self, lowFunc, highFunc):
        
        keypointList = [] #Initialize an empty list.
        for x in self.env.getXRange():
            (isKeypoint, score) = self.isKeypoint(x, highFunc, lowFunc)
            if isKeypoint:
                newKeyPoint = (x, (lowFunc[x] + highFunc[x])/2)
                keypointList.append(newKeyPoint)
                

        return keypointList

    #Helper function to check if x is a keypoint
    # Keypoints here mean sufficiently confident and overlapping the target value
    def isKeypoint(self, x, highFunc, lowFunc):
        #Needs to have one on each side
        if x < self.env.getXRange()[1] or x > self.env.getXRange()[-2]:
            return (False, None)
        funcRange = self.env.getMaxSample() - self.env.getMinSample()
        minimum   = self.env.getMinSample()

        leftDiff = ( highFunc[x-1] - lowFunc[x-1] )  / funcRange
        midDiff = ( highFunc[x] - lowFunc[x] )  / funcRange
        rightDiff = ( highFunc[x+1] - lowFunc[x+1] )  / funcRange

        if leftDiff > self.tolerance or midDiff > self.tolerance or \
           rightDiff > self.tolerance:
            totalDiff = max(leftDiff - self.tolerance,0) + max(midDiff - self.tolerance,0)+\
                        max(rightDiff - self.tolerance,0)
            return (False, totalDiff)
        
        leftScaled  = (( highFunc[x-1] + lowFunc[x-1] )/2 - minimum) / funcRange
        midScaled  = (( highFunc[x] + lowFunc[x] )/2 - minimum) / funcRange
        rightScaled      = (( highFunc[x+1] + lowFunc[x+1] )/2 - minimum) / funcRange
        
        #local max
        if midScaled >= leftScaled + self.tolerDiff and midScaled >= rightScaled + self.tolerDiff:
            return (True, None)

        # local min
        if midScaled <= leftScaled - self.tolerDiff and midScaled <= rightScaled - self.tolerDiff:            return (True, None)
        
        return (False, None) 
    
        
        return random.choice(self.env.getXRange())


    #Re-initializes the human sampler from scratch
    #Returns True if reset successful, False otherwise
    def tagOut(self):
        return True

    def buildTheoryFromInitialSamples(self, samples):
        return EmpTheoryGetter(self.env, samples)


def EmpTheoryGetter(environment, samples):
    samplesDict = {}
    for x,y in samples:
        if x not in samplesDict:
            samplesDict[x] = []
        samplesDict[x].append(y)
        
    avgDict = {}
    for x in samplesDict:
        avgDict[x] = sum(samplesDict[x])/len(samplesDict[x])

    finalDict = {}
    lastRealX = None
    #Linearlly interpolate
    for x in environment.getXRange():
        if x in avgDict:
            finalDict[x] = avgDict[x]
            lastRealX = x
        nextRealX = None
        for end in range(x+1, environment.getXRange()[-1]+1):
            if end in avgDict:
                nextRealX = end
                break
        if lastRealX is None and nextRealX is None:
            print("should not be possible!")
        elif lastRealX is None:
            #At beginning
            finalDict[x] = avgDict[nextRealX]
        elif nextRealX is None:
            # At end
            finalDict[x] = avgDict[lastRealX]
        else:
            ydiff = avgDict[nextRealX] - avgDict[lastRealX]
            gap = nextRealX-lastRealX
            pos = x - lastRealX
            newV = ((pos/gap) * ydiff) + avgDict[lastRealX]
            finalDict[x] = newV
    print(avgDict)
    print(finalDict)
    return finalDict
            
            

# Implements a dummy human that will select keypoints in locations
# that are "scientifically surprising", meaning that they are
# a certain distance away from a known "theory" function.
class DifferenceBasedHuman(humanSampler):
    #theoryFuncGetter is a python subroutine that given an env will give you a response function
    def __init__(self, theoryFuncGetter, distanceThresh):
        self.theoryFuncGetter = theoryFuncGetter
        self.distanceThresh = distanceThresh

    def initWithEnvironment(self,env):
        self.env = env
        return True



    def getUpdatedKeypoints(self, lowFunc, highFunc):
        keypointList = [] #Initialize an empty list.
        for x in self.env.getXRange():
            if self.isKeypoint(x, highFunc, lowFunc):
                newKeyPoint = (x, (lowFunc[x] + highFunc[x])/2)
                keypointList.append(newKeyPoint)
                

        return keypointList

    #Helper function to check if x is a keypoint
    # Keypoints here mean sufficiently confident and overlapping the target value
    def isKeypoint(self, x, highFunc, lowFunc):
        #if this returns true you are certain it is more than the min distance below the theory func        
        if highFunc[x] <= self.theoryFunc[x] - self.distanceThresh:
            return True
        #if this returns true you are certain it is more than the min distance above the theory func
        elif lowFunc[x] >= self.theoryFunc[x] + self.distanceThresh:
            return True
        return False


    def buildTheoryFromInitialSamples(self, samples):
        self.theoryFunc = self.theoryFuncGetter(self.env, samples)
        return self.theoryFunc


# Implements a dummy human that will select keypoints in locations
# where the function intersects a horizontal line at a specific y-value.
# Confidence Threshold(confThresh) is a single integer.
# confThresh is used to limit how large of a confidence interval we will check for
# intersections.
class SimilarPointsHuman(humanSampler):

    def __init__(self, targetLoYP, targetHiYP, tolerance):
        self.targetLoYP = targetLoYP
        self.targetHiYP = targetHiYP
        self.tolerance = tolerance

    def initWithEnvironment(self,env):
        self.env = env
        maxV = self.env.getMaxSample()
        
        self.targetLoY = self.env.getMinSample() + self.targetLoYP * (self.env.getMaxSample() - self.env.getMinSample())
        self.targetHiY = self.env.getMinSample() + self.targetHiYP * (self.env.getMaxSample() - self.env.getMinSample())
        return True

    def getUpdatedKeypoints(self, lowFunc, highFunc):
        keypointList = [] #Initialize an empty list.
        for x in self.env.getXRange():
            if self.isKeypoint(x, highFunc, lowFunc):
                newKeyPoint = (x, (lowFunc[x] + highFunc[x])/2)
                keypointList.append(newKeyPoint)
                

        return keypointList

    # Helper function to check if x is a keypoint.
    # Keypoints here mean sufficiently confident and 
    # overlapping the target value.
    def isKeypoint(self, x, highFunc, lowFunc):
        # if the midpoint is in and the ci is "small enough", mark it a keypoint
        # print("self.tolerance: ", self.tolerance)
        # Determine how to apply tolerance attribute to confidence interval.
            # We want to ID keypoints, faster.
            # make the sandwich happen, faster.
            # It has to be confident.
        # if (hix - lox) scaled separately to 0-1 is less than self.tolerance
            # then check midpoint swapped with highFunc[x] and lowFunc[x]
        funcRange = self.env.getMaxSample() - self.env.getMinSample()
        minimum   = self.env.getMinSample()
        hiScaled  = ( highFunc[x] - minimum    ) / funcRange
        loScaled  = (  lowFunc[x] - minimum    ) / funcRange
        midY      = ( highFunc[x] + lowFunc[x] ) / 2 
        hiLoDiff  = hiScaled - loScaled
        
        if hiLoDiff < self.tolerance:        
            if self.targetHiY >= midY:
                if midY >= self.targetLoY:
                    return True
        return False


    #Re-initializes the human sampler from scratch
    #Returns True if reset successful, False otherwise
    def tagOut(self):
        return True

    def buildTheoryFromInitialSamples(self, samples):
        return EmpTheoryGetter(self.env, samples)




