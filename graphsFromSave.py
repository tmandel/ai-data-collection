# This script creates and saves visualizations as *.png files
# using json data generated by simulations from graphs.py.

import matplotlib
from matplotlib import pyplot as plt
import json
import os, sys


#AI Tuples list (modified)
aiTuples =  [
                (None, "Round_Robin"),
                (None, "Epsilon_Greedy"),
                (None, "Thompson"),
                (None, "UWPS"),
                (None, "TESA-0"),
                (None, "TESA-10"),
                (None, "TESA-20"),
                (None, "Optimal")
            ]

#Modified Environment Tuples list.  
envTuples = [
                (
                    None, 
                    "Economics",
                    None,
                    "DifferenceBasedHuman", 
                    10000
                ),
                (
                    None,
                    "Economics", 
                    None,
                    "CriticalPointsHuman", 
                    10000
                ),
                (
                    None,
                    "Mental Health", 
                    None,
                    "SimilarPointsHuman", 
                    10000
                ),
                (
                    None,
                    "Mental Health", 
                    None,
                    "DifferenceBasedHuman", 
                    10000
                ),
                (
                    None,
                    "Psychology", 
                    None,
                    "SimilarPointsHuman", 
                    10000
                ),
                (
                    None,
                    "Psychology", 
                    None,
                    "CriticalPointsHuman", 
                    10000
                )
            ]


if __name__ == "__main__":
    
    matplotlib.rcParams['ps.useafm'] = True
    matplotlib.rcParams['pdf.use14corefonts'] = True
    #Used in the paper version but requires latex dependencies
    #matplotlib.rcParams['text.usetex'] = True
    matplotlib.rcParams.update({'font.size': 13})
    humanTuples = []
    evalTuples = []
    results = []
    env_num=0
    ai_num =0
    with open("allResults.json", "r") as f:
        allResults = json.load(f)


    ################### ENV LOOP START ################################################################################
    for env, envName, human, humanName, tlimit in envTuples:
        env_num+=1
        trange = range(tlimit)

        linestyleList=['p','<','D','x','*','o','v']
        i=0
        changeSpace=0
        ################################## AI LOOP START ########################################################
        for ai,aiName in aiTuples:
            ai_num+=1
            print("Human: ", humanName, "\nAI: ", aiName)
            
            keyStr = json.dumps((envName, humanName, aiName))
            avgResults = []
                
            maxCI = None
            for t in trange:
                (mean, ci) = allResults[keyStr][t]
                if maxCI is None or ci > maxCI:
                    maxCI = ci
                avgResults.append(mean)

            height=5000 #height of graph    
            if 'TESA' in aiName:
                print("MaxCI:", maxCI)
                print('Max%', maxCI/height)

            if aiName=='TESA-10': # change the brightness
                alpha=1.0
            elif aiName=='Optimal': # remove Optimal graphs
                continue
            else:
                alpha=0.6
                
            space=0.5 + changeSpace # change space between markers
            aiName = aiName.replace("_","-")
            plt.plot(trange, avgResults, label= aiName, markevery=space, markersize=10, marker=linestyleList[i], alpha=alpha)
            i+=1
            changeSpace+=0.03
        print()
        

        


        ################## CREATE AND SAVE PLOT ##################
        #Format and write out the plot
        plt.legend(loc='best')
        plt.xlabel("Timestep")
        plt.ylabel("Cumulative Regret") 
        plt.ylim([-100, height])
        plt.savefig(envName.replace("Mental Health", "MentalHealth") + "_" + humanName + ".pdf")
        plt.clf()
        plt.cla()
        plt.close()
