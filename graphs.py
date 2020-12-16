# This script runs simulations to compare AI algorithms.

from matplotlib import pyplot as plt
import aiSampler as ais
import humanSampler as hu
import environments as envs
import evaluators as eval
import cheater
import random
import json
import os, sys
import statsTrack as stat


def createVisualizationJson(lofunc,func,hifunc, t, envName, aiName, minValue, maxValue):
    dictionary = {'lofunc':lofunc, 'func':func, 'hifunc':hifunc, 'maxValue':maxValue, 'minValue':minValue}
    fileName = envName+'_'+aiName+'_'+str(t)+'.json'
    f = open('jsons'+os.sep+fileName, 'w')
    json.dump(dictionary, f)
    f.close()
    return

def getInitialSamples(env, numSamples):
    ret = []
    curX = 0
    for i in range(numSamples):
        curX = (curX + 7) % len(env.getXRange())
        x = curX
        (y, toProcess) = env.sample(x)
        ret.append((x,y))
    return ret


#Each graph is averaged over this many runs
NUM_ITERATIONS = 500

# Boolean flag that will tell the function whether
# to call out to the human for keypoints.
EVAL_IMMEDIATELY = True

# System will ask for human feedback after this many runs in the main loop.
ASK_PERIOD = 100

visualizeJson = False
epsilon = 0.1

#AI Tuples list (modified)
aiTuples =  [
                (ais.RoundRobinSampler(), "Round_Robin"),
                (ais.EpsilonGreedyKeyPointSampler(epsilon), "Epsilon_Greedy"),
                (ais.SimpleNNTSSampler(), "Thompson"),
                (ais.UWPSSampler(), "UWPS"),
                (ais.TESA(0), "TESA-0"),
                (ais.TESA(10), "TESA-10"),
                (ais.TESA(20), "TESA-20"),
                (ais.OptimalSampler(), "Optimal")
            ]

# Modified Environment Tuples list.
envTuples = [
                (
                    envs.DataDrivenEnv("Data/Avocado/avocadoFile.json"),
                    "Economics",
                    hu.DifferenceBasedHuman(hu.EmpTheoryGetter,100000),
                    "DifferenceBasedHuman",
                    10000
                ),
                (
                    envs.DataDrivenEnv("Data/Avocado/avocadoFile.json"),
                    "Economics",
                    hu.CriticalPointsHuman(0.7, 0.05),
                    "CriticalPointsHuman",
                    10000
                ),
                (
                    envs.DataDrivenEnv("Data/MentalHealth/mental_illness_file.json"),
                    "Mental Health",
                    hu.SimilarPointsHuman(0.0,0.33, 0.7),
                    "SimilarPointsHuman",
                    10000
                ),
                (
                    envs.DataDrivenEnv("Data/MentalHealth/mental_illness_file.json"),
                    "Mental Health",
                    hu.DifferenceBasedHuman(hu.EmpTheoryGetter,50),
                    "DifferenceBasedHuman",
                    10000
                ),
                (
                    envs.DataDrivenEnv("Data/psych/psychData.json"),
                    "Psychology",
                    hu.SimilarPointsHuman(0.1,0.5, 0.7),
                    "SimilarPointsHuman",
                    10000
                ),
                (
                    envs.DataDrivenEnv("Data/psych/psychData.json"),
                    "Psychology",
                    hu.CriticalPointsHuman(0.7,0.05),
                    "CriticalPointsHuman",
                    10000
                )
            ]

if __name__ == "__main__":
    random.seed(8721783) #Reproducibility
    humanTuples = []
    evalTuples = []
    results = []
    env_num=0
    ai_num =0
    allResults = {}

    ################### ENV LOOP START ################################################################################

    for env, envName, human, humanName, tlimit in envTuples:
        env_num+=1
        trange = range(tlimit)
        envReady = env.reset()
        if not envReady:
            print("Environment not ready, returning to top of loop.")
            continue

        evaluator = eval.RegretEvaluator()
        
        if isinstance(evaluator, cheater.Cheater):
            evaluator.passTrueEnvironment(env)

        huInited = human.initWithEnvironment(envs.MIEnvironmentInfo(env)) #Boolean, can be True or False.
        if not huInited:
            continue

        initSamples = getInitialSamples(env, 10)
        theory = human.buildTheoryFromInitialSamples(initSamples)

        evaluator.initWithEnvironment(envs.MIEnvironmentInfo(env))

        (loEvalFunc, hiEvalFunc) = evaluator.estimateFunction()
        trueKeypointsList = human.getUpdatedKeypoints(loEvalFunc, hiEvalFunc)
        while len(trueKeypointsList) == 0:
            human.tagOut()
            initSamples = getInitialSamples(env, 10)
            theory = human.buildTheoryFromInitialSamples(initSamples)
            (loEvalFunc, hiEvalFunc) = evaluator.estimateFunction()
            trueKeypointsList = human.getUpdatedKeypoints(loEvalFunc, hiEvalFunc)

        ################################## AI LOOP START ########################################################

        for ai,aiName in aiTuples:
            ai_num += 1
            print("Human: ", humanName, "\nAI: ", aiName)
            iterationCounter = 0
            failed = False
            totalLearnerResults = [0.0] * len(trange)
            allLearnerResults = []
            for t in trange:
                allLearnerResults.append(stat.StatsTracker())

            ####################### NUM ITERATIONS LOOP START ##############################################
            for it in range(NUM_ITERATIONS):
                iterationCounter += 1
                percentComplete = 100 * iterationCounter/NUM_ITERATIONS
                print("loading: ", percentComplete, "%" )



                ############################# RESET / INIT #############################

                # Set up the learner and the environment
                env.reset()
                human.tagOut()
                theory = human.buildTheoryFromInitialSamples(initSamples)
                ai.processPriorTheory(theory)

                inited = ai.initWithEnvironment(envs.MIEnvironmentInfo(env)) # Boolean, can be True or False.
                if not inited:
                    failed = True
                    break

                if isinstance(ai, cheater.Cheater):
                    ai.passTrueEnvironment(env)
                    ai.passTrueHuman(human)

                cumulativeScore = 0.0

                ########################################################### MAIN LOOP START #############################################################
                for t in trange:

                    chosenX = ai.chooseXValue()
                    (yValue, toProcess) = env.sample(chosenX)

                    # toProcess is a list.
                    for (xValue, yValue) in toProcess:
                        ai.processSample(xValue, yValue)
                        evaluator.processAISample(xValue, yValue)

                    # If True, call out to human for keypoints.
                    if EVAL_IMMEDIATELY:
                        evaluator.processKeypoints(trueKeypointsList)

                    if t % ASK_PERIOD == ASK_PERIOD - 1:
                        (lofunc,func,hifunc) = ai.generateVisualization()
                        minValue = env.getMinSample()
                        maxValue = env.getMaxSample()
                        if it==0 and visualizeJson==True and env_num==1 and ai_num==1:
                            createVisualizationJson(lofunc, func, hifunc, t, envName, aiName, minValue, maxValue)
                        keypointList = human.getUpdatedKeypoints(lofunc, hifunc)

                        ai.processKeyPoints(keypointList)
                        evaluator.processEmpiricalKeypoints(keypointList)

                        # In reality, getting keypoints will only occur once for human and evals.
                        if not EVAL_IMMEDIATELY:
                            (loEvalFunc, hiEvalFunc) = evaluator.estimateFunction()
                            keypointsList = human.getUpdatedKeypoints(loEvalFunc, hiEvalFunc)
                            evaluator.processKeypoints(keypointsList)

                    # Evaluator score only updates when a new keypoint updates.
                    cumulativeScore += evaluator.getCurrentScore()
                    totalLearnerResults[t] += cumulativeScore
                    allLearnerResults[t].update(cumulativeScore)

            if failed: # due to unimplemented learner
                print ("Learner unimplemented, moving to next learner.")
                continue # With next learner

            keyStr = json.dumps((envName, humanName, aiName))
            allResults[keyStr] = []
            for t in trange:
                allResults[keyStr].append((allLearnerResults[t].getMean(), allLearnerResults[t].getCI()))

    with open("allResults.json", "w") as f:
        json.dump(allResults, f)
