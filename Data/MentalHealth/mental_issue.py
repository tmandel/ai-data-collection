import matplotlib.pyplot as plt
import csv
import json

def strMaker(low, high, age_range):
    if (low, high)==age_range[0]:
        xRange= '< '+str(high)
    elif (low, high)==age_range[-1]:
        xRange= str(low)+'+'
    else:
        xRange= str(low)+' - '+str(high)
    return (xRange)

buckets = 13
issue = 'Mood Disorder (Depression, Bipolar Disorder, etc)'
title = 'Age vs Percentage of Tech Workers with a Mood Disorder'
low = 20
high = 20
oldest_age = 59
span = (oldest_age - low)/buckets
age_range = []
for i in range(buckets):
    high += span
    high = int(high)
    ageTuple=(low, high)
    age_range.append(ageTuple)
    low += span
    low = int(low)

csvFile = 'mental-heath-in-tech-2016_20161114.csv'
f = open(csvFile, 'r', encoding='utf-8')
reader = csv.DictReader(f)

dictAllData={}
dictSelfAnswer = {}
dictDiagnosis = {}
dictTotal = {}
for row in reader:
    age = int(row['What is your age?'])
    region = row['What country do you work in?']
    selfAnswer = row['Do you currently have a mental health disorder?']
    diagnosis = row['Have you been diagnosed with a mental health condition by a medical professional?']
    condition = row['If so, what condition(s) were you diagnosed with?']
    condition = condition.strip()
    
    for i in range(len(age_range)):
        ageRange=age_range[i]
        (low, high)=age_range[i]
        isInRange = False
        if i == 0 and age<high:
            isInRange = True
        elif i == len(age_range)-1 and low<=age:
            isInRange = True
        elif low<=age and age<high:
            isInRange = True

        isCondition=False
        isValid=False
        if isInRange and diagnosis == 'Yes':
            if '|' in condition:
                conditions = condition.split('|')
                if issue in conditions:
                    dictDiagnosis[ageRange]=dictDiagnosis.get(ageRange,0)+1
                    isCondition =True
            else:
                if issue in condition:
                    isCondition = True
                    dictDiagnosis[ageRange]=dictDiagnosis.get(ageRange,0)+1
        if isInRange:
            if diagnosis == 'Yes' and condition:
                isValid = True
            elif diagnosis == 'No':
                isValid = True
            if isValid:
                dictTotal[ageRange]=dictTotal.get(ageRange,0)+1
                xRange=strMaker(low, high, age_range)
                if xRange not in dictAllData:
                    dictAllData[xRange]=[]
                if isCondition:
                    dictAllData[xRange].append(100)
                else:
                    dictAllData[xRange].append(0)
f.close()

xValues=[]
yValues=[]
ageCount=[]
diagnosisCount=[]
totalList=[]
for ageRange in age_range:
    diagnosis = dictDiagnosis.get(ageRange,0)
    total = dictTotal.get(ageRange,0)
    if total>=10:
        diagnosisCount.append(diagnosis)
        totalList.append(total)

for low, high in age_range:
    rangeA = (low, high)
    diagnosis = dictDiagnosis.get(rangeA,0)
    total = dictTotal.get(rangeA,0)
    if total>=10:
        xRange=strMaker(low, high, age_range)
        xValues.append(xRange)
        percentage = 100*diagnosis/total
        yValues.append(percentage)
plt.bar(xValues, yValues)
plt.xticks(rotation=45)
plt.grid(alpha=0.3)
plt.ticklabel_format(style='plain', axis='y') 
plt.xlabel('Age ranges')
plt.ylabel('Percentage')
plt.title(title)
plt.tight_layout()
plt.savefig('mental_issues_graph.png')
plt.show()
plt.clf()

description = 'This data is based on the percentage of certain age groups' \
              'of tech industry workers who suffer from mood disorders. ' \
              'Based on your knowledge of psychology, '

dictionary =    {
                    'title': title,
                    'description': description,
                    'xVals': xValues,
                    'yVals': yValues,
                    'xlabel': 'Age Ranges',
                    'ylabel': 'Percentage',
                    'All_sample': dictAllData
                }


f = open('mental_illness_file.json', 'w')

json.dump(dictionary, f)

f.close()



