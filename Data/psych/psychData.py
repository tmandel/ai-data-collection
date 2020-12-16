import matplotlib.pyplot as plt
import numpy as np
import csv
import json

'''
1 "50 mm"
2 "53 mm"
3 "56 mm"
4 "59 mm"
5 "62 mm"
6 "65 mm"
7 "68 mm"
8 "71 mm"
9 "74 mm"
10 "77 mm"
11 "80 mm"
12 "83 mm"
'''


# The following paragraph is hard coded due to the unorganized data sets
sizeList= [50,53,56,59,62,65,68,71,74,77,80,83]
sizeDict={}
for i in range(12):
    ii= i+1
    sizeDict[ii]=sizeList[i]


f1 = open('pdpr99ve20_pd1.csv', 'r')
firstDict={} # size in unit of mm
totalDict={}
secondDict={} # size without units 1-5
totalDict2={}
thirdDict={}
totalDict3={}
sizeList=[]
num=-2
num2=-3
lastTrial = -1
reader = csv.DictReader(f1)

for row in reader:
    time = int(row['ZEIT']) # miliseconds
    size = int(row['REIZ'])
    anotherSize = int(row['URTEIL'])
    currentTrial = int(row['TRIAL'])
    convertedSize = sizeDict[size]
    if time == 0:
        continue
    if lastTrial > currentTrial:
        sizeList=[]
    lastTrial = currentTrial
    sizeList.append(convertedSize)
    if len(sizeList) < 2:
        continue
    if time >= 99999:
        continue
    currentSize = convertedSize
    previousSize = sizeList[num]
    #previous2Size= sizeList[num2]
    
    newXvalue = (currentSize - previousSize)
    
    if abs(newXvalue) > 18:
        continue
    totalDict[newXvalue]=totalDict.get(newXvalue,0)+1
    firstDict[newXvalue]=firstDict.get(newXvalue, 0)+time
    
f1.close()


dictAllData={}
xValues=[]
yValues=[]
for size in sorted(totalDict):
    averageJudge = firstDict[size] / totalDict[size]
    size = str(size)
    xValues.append(size)
    yValues.append(averageJudge)
    if size not in dictAllData:
        dictAllData[size] = []
    dictAllData[size].append(averageJudge)
plt.bar(xValues, yValues)
plt.ylim(900,1200)
plt.grid(alpha = 0.3)
plt.ylabel('average time (miliseconds)')
plt.xlabel('size (mm)')
plt.title('Psych experiment')
plt.savefig('psychFigure.png')
plt.show()
plt.clf()

description = 'this is the data from an experiment ' \
              'in which peole are asked to judge ' \
              'the size of the sequence of the square.  ' \
              'This data gives ' \
              'the average reaction time on the y axis ' \
              'and the size in mm5'

dictionary =    {
                    'title':'Psychology Experiment',
                    'description': description,
                    'xVals': xValues,
                    'yVals': yValues,
                    'xlabel': 'Size Difference Between Squares (mm)',
                    'ylabel': 'Average Reaction Time (ms)',
                    'All_sample': dictAllData
                }

f = open('psychData.json', 'w')

json.dump(dictionary, f)

f.close()

