import matplotlib.pyplot as plt
import csv
import json

def currencyFormatter(currencyValue):
    """
    This function takes a decimal value and 
    normalizes it to be a string representing currency.
    """
    return "${:,.2f}".format(currencyValue)

csvFile = 'avocado.csv'
buckets = 20
selectedRegion = 'TotalUS'
selectedtype = 'organic'


f = open(csvFile, 'r')
reader = csv.DictReader(f)
priceList=[]
for row in reader:
    region =row['region']
    type_ = row['type']
    price = float(row['AveragePrice'])
    if region == selectedRegion and type_ == selectedtype:
        priceList.append(price)
        
# The following paragraph creates a tuple list of price ranges
maxPrice = max(priceList)
minPrice = min(priceList)
priceList=[]
rangeLow = 1.15
rangeHigh= 1.15
for i in range(buckets):
    if not rangeLow>maxPrice:
        separation = (maxPrice-minPrice)/buckets
        rangeHigh+= separation
        rangeHigh=round(rangeHigh, 2) # round up due to floating-point numbers calculation
        priceRange=(rangeLow, rangeHigh)
        priceList.append(priceRange)
        rangeLow+= separation
        rangeLow= round(rangeLow, 2)
f.close()

dictRegion={}
dictAllData = {}
f = open(csvFile, 'r')
reader = csv.DictReader(f)
soldDictTotal={}# incluses 2015 - 2018
soldDictNum ={}
for row in reader:
    price = float(row['AveragePrice'])
    numSold=float(row['Total Volume'])
    type_ = row['type']
    region =row['region']
    date=row['Date']
    for low, high in priceList:
        if low<=price and price<high and region == selectedRegion and type_ == selectedtype: # total
            priceRange=(low, high)
            soldDictTotal[priceRange]=soldDictTotal.get(priceRange,0)+numSold
            soldDictNum[priceRange]=soldDictNum.get(priceRange,0)+1
            xRange = currencyFormatter(low) + ' - ' + currencyFormatter(high)
            if xRange not in dictAllData:
                dictAllData[xRange] = []
            dictAllData[xRange].append(numSold)
        if date == '2018-03-11' and region == selectedRegion and type_ ==  selectedtype:
            print(region, type_, numSold)
            
f.close()

    
xValues=[]
yValues=[]
for low, high in priceList:
    # Normalize low & high to double precision and prepend '$'.
    xRange = currencyFormatter(low) + ' - ' + currencyFormatter(high)
    xValues.append(xRange)
    priceRange=(low, high)
    try: # denominator can be zero
        yAverage= soldDictTotal[priceRange]/soldDictNum[priceRange]
        yValues.append(yAverage)
    except:
        yAverage= 0
        yValues.append(yAverage)
plt.bar(xValues, yValues)
plt.xticks(rotation=90)
plt.grid(alpha=0.3)
plt.ticklabel_format(style='plain', axis='y') 
#plt.legend(loc='best')
#plt.xlim('1.15 - 1.2', '1.95 - 2.0')
xlabel = 'Price ($)'
ylabel = 'Average Weekly Num of Sold Avocados'
title = 'Price vs. Average Weekly Number of Sold Avocados'
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.title(title)
plt.tight_layout()
plt.savefig('avocado_sales.png')
plt.show()
plt.clf()


dictionary =    {
                    'title': title,
                    'description':'This is data on the average weekly num of avocados' \
                        ' sold at different prices. Based on your experience, ' \
                        'shopping for produce, ',
                    'xVals': xValues,
                    'yVals': yValues,
                    'xlabel': xlabel,
                    'ylabel': ylabel,
                    'All_sample': dictAllData
                }

f = open('avocadoFile.json', 'w')

json.dump(dictionary, f)

f.close()

