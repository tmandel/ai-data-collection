import cheater
import distributions as dists
import environments as envs
import math
import random
import sys
import utilities as util
import visualizers as vis

# Interface (abstract) for aiSampler objects.
class AISampler(object):

    # Re-initilializes with a given MIEnvironment
    # Returns True if initialization was successful, False otherwise
    def initWithEnvironment(self,env):
        pass

    def chooseXValue(self):
        pass

    # Processes a sample from environment.
    # Takes in a single xValue(int), and a single yValue(double)
    def processSample(self, xValue, yValue):
        pass

    # Process prior theory
    def processPriorTheory(self):
        pass

    # Takes in current keypoints.
    # Keypoints are a list of tuples: [(x,y),(x,y),(x,y)...]
    def processKeyPoints(self,currentKeypoints):
        pass

    # Returns a tuple of functions(lofunc, function,hifunc)
    # All functions should be dictionaries (x maps to y)
    # "function" is the measured response function.
    # It is guaranteed that lowfunc(x) <= func(x) <= hifunc(x).
    # Returned tuple wil be used for visualizations.
    def generateVisualization(self):
        pass

# A sampler that samples epsilon-greedy with respect to the existing keypoints
# (ignores samples received so far,
# other than to generate a visualization)
class EpsilonGreedyKeyPointSampler(AISampler):

    def __init__(self, epsilon):
        self.functionVisualizer = vis.BasicVisualizer(0.1)
        self.Epsilon = epsilon

    def initWithEnvironment(self,env):
        self.env = env
        self.functionVisualizer.initWithEnvironment(env)
        self.KeyPoints = []
        return True

    def chooseXValue(self):
        if random.random() < self.Epsilon:
            return random.choice(self.env.getXRange())
        if(len(self.KeyPoints) == 0):
            return random.choice(self.env.getXRange())
        (x, y) = random.choice(self.KeyPoints)
        return x

    def processSample(self, xValue, yValue):
        return self.functionVisualizer.processSample(xValue, yValue)

    # Takes in current keypoints.
    # Keypoints are a list of tuples: [(x,y),(x,y),(x,y)...]
    def processKeyPoints(self,currentKeypoints):
        self.KeyPoints = currentKeypoints

    # Returns a tuple of functions(function, hifunc, lowfunc)
    # All functions should be dictionaries (x maps to y)
    # "function" is the measured response function.
    # It is guaranteed that lowfunc(x) <= func(x) <= hifunc(x).
    # Returned tuple wil be used for visualizations.
    def generateVisualization(self):
        return self.functionVisualizer.generateVisualization()

    # Process prior theory (needed for previous pipeline)
    def processPriorTheory(self, theoryFunc):
        pass

# A sampler that blindly round-robins among x values
class RoundRobinSampler(AISampler):

    def __init__(self):
        self.functionVisualizer = vis.BasicVisualizer(0.1)

    def initWithEnvironment(self,env):
        self.env = env
        self.functionVisualizer.initWithEnvironment(env)
        self.index = 0
        return True

    def chooseXValue(self):
        ret = self.index
        self.index = (self.index + 1) % len(self.env.getXRange())
        return ret

    def processSample(self, xValue, yValue):
        return self.functionVisualizer.processSample(xValue, yValue)

    # Takes in current keypoints.
    # Keypoints are a list of tuples: [(x,y),(x,y),(x,y)...]
    def processKeyPoints(self,currentKeypoints):
        pass

    # Returns a tuple of functions(function, hifunc, lowfunc)
    # All functions should be dictionaries (x maps to y)
    # "function" is the measured response function.
    # It is guaranteed that lowfunc(x) <= func(x) <= hifunc(x).
    # Returned tuple wil be used for visualizations.
    def generateVisualization(self):
        return self.functionVisualizer.generateVisualization()

    # Process prior theory
    def processPriorTheory(self, theoryFunc):
        pass


class SimpleNNTSSampler(AISampler):
    def __init__(self):
        self.functionVisualizer = vis.BasicVisualizer(0.1)


    def initWithEnvironment(self,env):
        self.env = env
        self.functionVisualizer.initWithEnvironment(env)
        self.ks = [0] * len(self.env.getXRange())
        self.mus = [0] * len(self.env.getXRange())
        self.samples = {}
        for x in self.env.getXRange():
            self.samples[x] = []
        self.keypoints = []
        self.rawKeyPoints = []
        oldCI = util.getCI([], 0.1)
        newCI = util.getCI([1], 0.1)
        k = len(self.env.getXRange())
        self.maxReward = (k/newCI - k/oldCI)
        return True

    def getReward(self, xValue, samples, newSample):
        # Existing keypoints: clear (additional score from extra sample)
        # new keypoints: doesn't consider for simplicity
        # max - min
        oldScore = util.getEvalScore(self.samples, self.rawKeyPoints, 0.1)
        self.samples[xValue].append(newSample)
        newScore = util.getEvalScore(self.samples, self.rawKeyPoints, 0.1)
        self.samples[xValue].pop()
        reward = newScore - oldScore

        maxReward = self.maxReward
        minReward = -1
        if reward > maxReward + 0.000001 or reward < minReward - 0.000001:
            print("out of range reward!", reward)
            sys.exit(1)

        normR =  (reward-minReward)/(maxReward - minReward)

        if normR > 1.000001 or normR < -0.000001:
            print("out of range reward!", normR)
            sys.exit(1)
        return normR

    def chooseXValue(self):
        maxY = None
        maxX = None
        for x in self.env.getXRange():
            sigma = math.sqrt(1/(self.ks[x] +1))
            nDist = dists.NormalDistribution(self.mus[x], sigma)
            y = nDist.sample()
            if maxY is None or y > maxY:
                maxY = y
                maxX = x
        return maxX

    #called before processkeypoints
    def processSample(self, xValue, yValue):
        oldtotal = self.mus[xValue] * self.ks[xValue]
        self.ks[xValue] += 1
        r = self.getReward(xValue, self.samples[xValue], yValue)
        self.mus[xValue] = (oldtotal+r)/(self.ks[xValue])
        self.samples[xValue].append(yValue)
        return self.functionVisualizer.processSample(xValue, yValue)

    # determines the reward in terms of keypoint
    def processKeyPoints(self,currentKeypoints):
        self.rawKeyPoints = currentKeypoints
        pass

    # Returns a tuple of functions(function, hifunc, lowfunc)
    # All functions should be dictionaries (x maps to y)
    # "function" is the measured response function.
    # It is guaranteed that lowfunc(x) <= func(x) <= hifunc(x).
    # Returned tuple wil be used for visualizations.
    def generateVisualization(self):
        return self.functionVisualizer.generateVisualization()

    def processPriorTheory(self,theoryFunc):
        pass

# Uncertainty Weighted Posterior Sampling
class UWPSSampler(AISampler):
    # Idea: Sample to get distance from prior theory
    # Do that multipled by uncertainty to pick which arm to sample
    # Exponents control weighting.
    def __init__(self):
        self.functionVisualizer = vis.BasicVisualizer(0.1)

    def initWithEnvironment(self,env):
        self.env = env
        self.functionVisualizer.initWithEnvironment(env)
        self.ks = [0] * len(self.env.getXRange())
        self.mus = [0] * len(self.env.getXRange())
        self.samples = {}
        for x in self.env.getXRange():
            self.samples[x] = []
        self.keypoints = []
        self.rawKeyPoints = []
        return True

    def chooseXValue(self):
        maxScore = None
        maxX = None
        for x in self.env.getXRange():
            sigma = math.sqrt(1/(self.ks[x] +1))
            nDist = dists.NormalDistribution(self.mus[x], sigma)
            y = nDist.sample()
            priorY = (self.priorTheory[x] - self.env.getMinSample()) / (self.env.getMaxSample() - self.env.getMinSample())
            diff = abs(y - priorY)
            uncertainty = 1/(self.ks[x] +1)
            score = diff * uncertainty
            if maxScore is None or score > maxScore:
                maxScore = score
                maxX = x
        return maxX

    #called before processkeypoints
    def processSample(self, xValue, yValue):
        oldtotal = self.mus[xValue] * self.ks[xValue]
        self.ks[xValue] += 1
        transYVal = (yValue - self.env.getMinSample()) / (self.env.getMaxSample() - self.env.getMinSample())
        if transYVal < 0 or transYVal > 1:
            print("Y out of range! ", yValue)
            sys.exit(1)
        self.mus[xValue] = (oldtotal+transYVal)/self.ks[xValue]
        self.samples[xValue].append(transYVal)
        return self.functionVisualizer.processSample(xValue, yValue)

    def processKeyPoints(self,currentKeypoints):
        #ignore keypoints
        pass


    # Returns a tuple of functions(function, hifunc, lowfunc)
    # All functions should be dictionaries (x maps to y)
    # "function" is the measured response function.
    # It is guaranteed that lowfunc(x) <= func(x) <= hifunc(x).
    # Returned tuple wil be used for visualizations.
    def generateVisualization(self):
        return self.functionVisualizer.generateVisualization()

    def processPriorTheory(self,theoryFunc):
        self.priorTheory = theoryFunc


class OptimalSampler(AISampler, cheater.Cheater):

    def __init__(self):
        self.functionVisualizer = vis.BasicVisualizer(0.1)

    def initWithEnvironment(self,env):
        self.env = env
        self.funcSamples = []
        self.functionVisualizer.initWithEnvironment(env)
        self.keypointTracker = None
        self.keypoints = None
        self.truFunc = None # see passTrueEnvironment
        # Track samples per x coordinate.
        self.samples = {}
        for x in self.env.getXRange():
            self.samples[x] = []

        return True

    def chooseXValue(self):
        """
        This function returns the x value
        of the least sampled keypoint.
        """
        return util.chooseOptimalXValue(self.keypoints, self.samples)

    def passTrueHuman(self, human):
        """
        A setter, receiving a human object for getting keypoints
            for optimal sampling.
        Param(s):
            self:   an OptimalSampler object,
            human:  a human object for processing functions, which, here
                        are a dicitonary of coordintates, e.g.:
                        {x: y, x: y, x: y, ...}.
        Returns:
            None
        """
        # pass (hi/lo)/truFunc to human. hi/lo should be the same, by now.
        self.keypoints = human.getUpdatedKeypoints(self.truFunc, self.truFunc)

    def passTrueEnvironment(self, trueEnvironment):
        # Change env from MIEnvironmentInfo object to MIEnvironment object
        # for accessing se
        # self.env = trueEnvironment
        # get the trufunc from the environment
        # hi/lo are same function -> truFunc
        # truFunc is a dict: {x: y, x: y, x: y, ...}. The x's are ints.
        self.truFunc = trueEnvironment.generateTrueFunction()

    def processSample(self, xValue, yValue):
        self.samples[xValue].append(yValue)
        return self.functionVisualizer.processSample(xValue, yValue)

    # Process prior theory
    def processPriorTheory(self, theoryFunc):
        pass

    # Takes in current keypoints.
    # Keypoints are a list of tuples: [(x,y),(x,y),(x,y)...]
    def processKeyPoints(self,currentKeypoints): #Is implemented correctly!
        pass

    # Returns a tuple of functions(lofunc,func,hifunc)
    # All functions should be dictionaries (x maps to y)
    # "function" is the measured response function.
    # It is guaranteed that lowfunc(x) <= func(x) <= hifunc(x).
    # Returned tuple wil be used for visualizations.
    def generateVisualization(self):
        return self.functionVisualizer.generateVisualization()


class TESA(AISampler):
    """
    This algorithm aims to sample at the most promising x values.
    Four general steps are used to determine where to sample:
        (1) Estimate how much data is needed to identify a keypoint
            using a Pareto distribution P (conjugate to Uniform
            with unknown max).
        (2) Sample P every timestep to get a threshold on how much
            data is needed to identify a keypoint.
        (3) With probability epsilon_p OR
            when the least sampled x value is above the threshold,
            select an x value that has been previously identified as a
            keypoint.  When a keypoint is selected, it is the keypoint
            with the least samples, so far. (TESA NEVER selects an x value with
            more samples than the threshold, unless it is a keypoint.)
        (4) If neither of the two conditions in case (3) are met,
            select an x value that has been sampled the least.
    """
    def __init__(self, scale):
        self.functionVisualizer = vis.BasicVisualizer(0.1)
        self.xM = scale  #scale

    # Re-initilializes with a given MIEnvironment
    # Returns True if initialization was successful, False otherwise
    def initWithEnvironment(self,env):
        self.env = env
        self.functionVisualizer.initWithEnvironment(env)
        self.keypoints = []

        self.k = 1  #shape, sometimes called a

        # hard-coded probability for determining whether we
        # are more interested in sampling keypoints, or non keypoints.
        self.epsilon_p = 0.1

        # key point start samples tracks how many samples
        # had been conducted at a given x value when it
        # was identified as a keypoint. The keys are the x coordinate
        # and the values are the quantity of samples. That is, it's a
        # dict mapping from x value of keypoint --> # of samples when
        # it was made a keypoint
        self.kpStartSamples = {}

        # A growing dictionary of all samples at each x value.
        self.samples = {}
        # OriGinal samples
        self.ogSamples = {}

        # Populate initialization variables in accordance
        # with the environmentally dependent quantity of x coordinates.
        for x in self.env.getXRange():
            self.samples[x] = []
            self.kpStartSamples[x] = None
            self.ogSamples[x] = 0

        return True


    def chooseXValue(self):
        """
        chooseXValue returns an x coordinate that might
        be identified as a keypoint in the future.
        """
        # Determine posterior hyperparameters for Pareto Distribution
        maxXm = self.xM  # max start time for a keypoint (posterior value)
        for x in self.keypoints:
            xN = self.kpStartSamples[x]
            if xN > maxXm:
                maxXm = xN

        shape = self.k + len(self.keypoints)
        scale = maxXm
        # Construct pareto posterior distribution
        paretoDist = dists.ParetoDistribution(shape, scale)
        # Sample the distribution
        threshold = paretoDist.sample()
        # Feed Pareto distro sample to below getProb

        minKp = None
        i_k = None
        minSamp = None
        i_h = None
        for i in self.env.getXRange():
            # we want number of samples now, regardless of keypoint id-ness
            sampleQuantity = len(self.samples[i])
            # Determine whether we are iterating over keypoints or
            # x values that are not keypoints.
            if i in self.keypoints:
                if minKp is None or sampleQuantity < minKp:
                    minKp = sampleQuantity
                    i_k = i

            if minSamp is None or sampleQuantity < minSamp:
                minSamp = sampleQuantity
                i_h = i

        if len(self.keypoints) >0 and i_k is None:
            print("error!  i_k is None!")
            print("We have", len(self.keypoints), "compared to", len(self.env.getXRange()))

        if i_h is None:
            print("error!  i_h is None!")
            print("We have", len(self.keypoints), "compared to", len(self.env.getXRange()))

        r = random.random()

        chosenX = None
        if len(self.keypoints) > 0 and \
           (r >= self.epsilon_p or  \
                (minSamp is not None and minSamp >= threshold)):
            chosenX = i_k
        else:
            chosenX = i_h

        return chosenX

    # Processes a sample from environment.
    # Takes in a single xValue(int), and a single yValue(double)
    def processSample(self, xValue, yValue):
        self.samples[xValue].append(yValue)
        return self.functionVisualizer.processSample(xValue, yValue)

    # Process prior theory
    def processPriorTheory(self, theoryFunc):
        self.priorTheory = theoryFunc

    # Takes in current keypoints.
    def processKeyPoints(self,currentKeypoints):
        """
        Updates a dict mapping x vals to the quantity of samples at that x val
        when that x val was first identified as a keypoint.
        Param(s):
            self:               a TESA object.
            currentKeypoints:   x,y coordinate pairs, a list of tuples,
                                arranged thusly: [ (x,y), (x,y), (x,y), ... ]
                                x is <class 'int'> and y is <class 'float'>.
        Returns: None
        """
        removedKeypoints = []
        newKeypoints = []
        newestKeypoints = False
        currentXPoints = [x for (x,y) in currentKeypoints]

        # Determine whether this is our first collection of keypoints.
        if len(self.keypoints) == 0:
            # All of these keypoints are original.
            newKeypoints = currentXPoints
            newestKeypoints = True
        else:
            for x in currentXPoints:
                if x not in self.keypoints:
                    newKeypoints.append(x)
            for x in self.keypoints:
                if x not in currentXPoints:
                    removedKeypoints.append(x)

        # Update tracker for quantity of samples per x value.
        # Do not update keypoints a second time (unless removed).
        for x in self.env.getXRange():
            if x in newKeypoints:
                self.kpStartSamples[x] = (len(self.samples[x]) + self.ogSamples[x] ) / 2

            if x in removedKeypoints:
                # Reset sample tracker - not required, but safer.
                self.kpStartSamples[x] = None

            self.ogSamples[x] = len(self.samples[x])
        self.keypoints = currentXPoints

    # Returns a tuple of functions(lofunc, function, hifunc)
    # All functions should be dictionaries (x maps to y)
    # "function" is the measured response function.
    # It is guaranteed that lowfunc(x) <= func(x) <= hifunc(x).
    # Returned tuple wil be used for visualizations.
    def generateVisualization(self):
        return self.functionVisualizer.generateVisualization()






















