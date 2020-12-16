import math

#Takes in a sample list and returns the confidence variable over the list of samples.
def getCI(listofSamples, delta):
    sampleCount = len(listofSamples)
    
    sampleCount += 0.01
    #v = math.sqrt( (math.log(2/delta)) /(2*sampleCount) )
    #print("getCi : ", v, "sample no = ", sampleCount)
    return math.sqrt( (math.log(2/delta)) /(2*sampleCount) )

#Takes a Y value and clamps it to the range allowed by the environment
def clampY(env,yVal):
    if yVal < env.getMinSample():
        return env.getMinSample()
    elif yVal > env.getMaxSample():
        return env.getMaxSample()

    return yVal


def chooseOptimalXValue(keypoints, samples):
    """
    This method returns the optimal x value to sample next, given
    an existing set of samples.
    
    Param(s):
        keypoints:  a list of tuples of x,y coordinate pairs.
        samples:    a 2D list of y values per x value.
                    E.g., [ [y,y,y,y,y], [y,y], [y,y,y,y] ]
                    The indices are the x values.
    Returns:
        minSampsX:  an int, representing the x coordinate 
                    that has been sampled the least, so far. 
    """       
    # The x coordinate of the keypoint that has been sampled the least.
    minSampsX = None
    # The quantity of samples at minSampsX.
    minSamps  = None
    
    # Iterate over keypoints.
    for kpIdx in range(len(keypoints)):
        # x coordinate at a keypoint.
        x = keypoints[kpIdx][0]
        # The quantity of samples at the keypoint.
        sampQuant = len(samples[x])
        # Identify the least sampled keypoint.
        if minSamps is None or sampQuant < minSamps:
            minSampsX = x
            minSamps  = sampQuant
    # Return the x coordinte (int) of the least sampled keypoint.        
    return minSampsX

def getEvalScore(samples, currentKeypoints, delta):
    k = len(currentKeypoints)
    if k == 0:
        return 0.0
    
    CISum = 0.0
    CISum2 = 0.0
    ValSum = 0.0
    keypointXes = []

    maxCI = 1 # util.getCI([], self.getScientistPreferredCILevel())
    #print('biggest ci', util.getCI([1], self.getScientistPreferredCILevel()))
    for keypoint in currentKeypoints:
        (xValue, yValue) = keypoint
        keypointXes.append(xValue)
        # ck is Confidence at Keypoint
        # normally between zero and infinity
        # Loose bounds leave this as an initially large confidence interval.
        ck = getCI(samples[xValue], delta)
        #print("ck: ", ck)
        ck2 = min(ck, 1)

        val = max(maxCI - ck2, 0)
        ValSum += val
        CISum += ck
        CISum2 += 1.0/ck
    
    #self.score = float(k/CISum)
    
    
    # self.samples looks like [ [y,y,y,y], [y,y,y], [y,y,y,y,y,y,y,y], [y,y] ]
    #   The indices are x values. At each index, there is a list of y values.
    # Subtract a value from this score that accounts for
    # places that have been sampled that did not have a keypoint.
    
    penaltySum = 0.0
    nonPenaltySum=0.0
    for x in range(len(samples)):
        if x not in keypointXes:
            penaltySum += len(samples[x])
        else:
            nonPenaltySum += len(samples[x])
    
    # k is the quantity of keypoints
    score = float(k/CISum) - float(penaltySum)

    #score = CISum2 - float(penaltySum)
    return score
    
