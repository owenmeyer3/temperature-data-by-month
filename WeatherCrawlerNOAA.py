# Import =======================================================================
import math
import requests
from functions.dateFuncs import stampToHour
from functions.matrixFuncs import readcsv, clean_csv, saveCSV
from functions.tempFuncs import CtoF, wetBulbFunc
import numpy as np
from datetime import datetime, timedelta

# Query Settings ================================================================
# ASHRAE 2013: 1986-2010
# ASHRAE 2013: 1990-2014
location = "72530094846" # New York
location_2 = "" #Backup weather station if weather station has 2 codes (codes have chaned over time)
start_year = 1990
end_year = 2014
Psta = 14.7
primaryTemp = "DB"

# For each year =================================================================
# Make structured array to hold all final weatherdata spearated in monthly bins
dtype1=[('stamp', '<i4'), ('DB', '<f8'), ('DP', '<f8'), ('WB', '<f8')]
emptyArray = np.empty(4, dtype=dtype1)
yearsData = [{'data' :emptyArray, 'months' : 0}, {'data' : emptyArray, 'months' : 0}, {'data' : emptyArray, 'months' : 0}, {'data' : emptyArray, 'months' : 0},
            {'data' : emptyArray, 'months' : 0}, {'data' : emptyArray, 'months' : 0}, {'data' : emptyArray, 'months' : 0}, {'data' : emptyArray, 'months' : 0},
            {'data' : emptyArray, 'months' : 0}, {'data' : emptyArray, 'months' : 0}, {'data' : emptyArray, 'months' : 0}, {'data' : emptyArray, 'months' : 0}
            ]

# Get data for a year. Find temp values for each hour of the year. Check for month validity before adding to monthly data to yearsData.
for year in range(start_year, end_year + 1):
    print('Loading Year: ' + str(year))
    # Try retriving data from either primary or secondary source
    url="https://www.ncei.noaa.gov/data/global-hourly/access/"+str(year)+"/"+str(location)+".csv"
    url_2="https://www.ncei.noaa.gov/data/global-hourly/access/"+str(year)+"/"+str(location_2)+".csv"
    try:
        print("accessing: " + url)
        csv_retrieved = requests.get(url).content
    except: 
        try:
            print("accessing: " + url_2)
            csv_retrieved = requests.get(url_2).content
        except:
            print("Cannot access station data")

    # Name and save data as csv
    csv_address_to_save='weatherData/weather'+str(location)+str(year)+'.csv'
    with open(csv_address_to_save, 'wb') as f:
        f.write(csv_retrieved)
    
    # Convert data from csv to array
    data = readcsv(csv_address_to_save)
    saveCSV(data,'results/read')
    data = clean_csv(data)
    saveCSV(data,'results/cleaned')

    # Get start/end stamps of year
    yearStartStamp = int((datetime(start_year, 1, 1) - datetime(1970, 1, 1)) / timedelta(seconds=1))
    yearEndStamp = int((datetime(end_year+ 1, 1, 1) - datetime(1970, 1, 1)) / timedelta(seconds=1))
    
    # Write data for each hour of the year (if data not recorded on the hour, allow data within 0.5 hr)
    nearHourData = []
    for t in range(yearStartStamp, yearEndStamp, 3600):
        # Find closest date index to value
        nearest_i = (np.abs(data['stamp'] - t)).argmin()
        nearest_stamp = data['stamp'][nearest_i]
        nearest_row = data[nearest_i]
        DBf = CtoF(nearest_row[1])
        DPf = CtoF(nearest_row[2])
        # Add data to hour if data is marked within 0.5 hour difference
        if abs(nearest_stamp - t) <= 1800:
            nearHourData.append([t, DBf, DPf, wetBulbFunc(DBf, DPf, Psta)])
    saveCSV(nearHourData,'results/nearHourData')

    # Fill gaps of unrecorded hours with linearly interpolated data if timespan is less than 6 hours
    fillHourData = []
    for i, row in enumerate(nearHourData):
        if i == 0:
            continue
        # Test if gap between hours is less than 6 hours
        thisStamp = nearHourData[i][0]
        lastStamp = nearHourData[i-1][0]
        stampDiff = thisStamp - lastStamp
        if stampDiff <= 21600 and stampDiff > 3600:
            #Gget data from hours around gap
            thisDB = nearHourData[i][1]
            lastDB = nearHourData[i-1][1]
            DBDiff =  thisDB - lastDB
            thisDP = nearHourData[i][2]
            lastDP = nearHourData[i-1][2]
            DPDiff =  thisDP - lastDP
            thisWB = nearHourData[i][3]
            lastWB = nearHourData[i-1][3]
            WBDiff =  thisWB - lastWB
            # Create interpolated hour data
            for s in range(lastStamp + 3600, thisStamp, 3600):
                DBinterp = (DBDiff)/(stampDiff)*(s-lastStamp) + lastDB
                DPinterp = (DPDiff)/(stampDiff)*(s-lastStamp) + lastDP
                WBinterp = (WBDiff)/(stampDiff)*(s-lastStamp) + lastWB
                fillHourData.append([s, DBinterp, DPinterp, WBinterp])
    # If interpolate hour data was created, add it to the hour data
    if fillHourData:
        hourlyData = np.append(nearHourData, fillHourData, axis=0)
    else:
        hourlyData = np.array(nearHourData)

    # Create structured array of stamp, DB, DP, WB for each hour
        # Get hour data columns
    np_date_stamps = np.array(list(map(lambda x: int(x), hourlyData[:,0])))
    np_DBs = np.array(list(map(lambda x: float(x), hourlyData[:,1])))
    np_DPs = np.array(list(map(lambda x: float(x), hourlyData[:,2])))
    np_WBs = np.array(list(map(lambda x: float(x), hourlyData[:,3])))
        # Create an empty structured array
    dtype = np.dtype(dict(names=['stamp', 'DB', 'DP', 'WB'], formats=[arr.dtype for arr in (np_date_stamps, np_DBs, np_DPs, np_WBs)]))
    rows = hourlyData.shape[0]
    hourlyData = np.empty((rows), dtype=dtype)
        # Populate the structured array with the data from hour data
    hourlyData['stamp'], hourlyData['DB'], hourlyData['DP'], hourlyData['WB'] = np_date_stamps.T, np_DBs.T, np_DPs.T, np_WBs.T
    # Sort hourly data array
    np.sort(hourlyData, order='stamp') 
    saveCSV(hourlyData,'results/dataFilled')

    # Test each month for validity and add this year's hourly data to all year hourly data
    # Month is valid if: >85% of month hours exist AND abs(dayHours - nightHours) < 60)
    for month in range(1,13):
        monthIndex = month - 1
        nextMonth = month + 1
        nextMonthYear = year
        if month == 12:
            nextMonth = 1
            nextMonthYear = year + 1
        # Get the total hours in this month
        monthStartStamp = (datetime(year, month, 1) - datetime(1970, 1, 1)) / timedelta(seconds=1)
        monthEndStamp = (datetime(nextMonthYear, nextMonth, 1) - datetime(1970, 1, 1)) / timedelta(seconds=1)
        hoursInMonth = (monthEndStamp - monthStartStamp) / 3600
        # Get number of hours recorded this month
        thisMonthsRecords = hourlyData[(hourlyData['stamp']  >= monthStartStamp) & (hourlyData['stamp']  < monthEndStamp)]
        thisMonthsHours = len(thisMonthsRecords['stamp'])
        # Get number of day and night hours recorded this month
        thisMonthsHourRecords = np.array(list(map(lambda x: stampToHour(x), thisMonthsRecords['stamp'])))
        thisMonthsDayHours = len([i for i in thisMonthsHourRecords if i >= 6 and i < 18 ])
        thisMonthsNightHours = thisMonthsHours - thisMonthsDayHours
        # Add months hour data if month is valid
        if thisMonthsHours / hoursInMonth >= 0.85 and abs(thisMonthsDayHours - thisMonthsNightHours) <= 60:
            yearsData[monthIndex]['months'] += 1
            yearsData[monthIndex]['data'] = np.append(yearsData[monthIndex]['data'], thisMonthsRecords, axis=0)
 
# Take data from all years and create final report =============================
# Set mean coincedent temperatures based on user-input primary temperature
if primaryTemp == 'DB':
    secondaryTemp1 = 'DP'
    secondaryTemp2 = 'WB'
elif primaryTemp == 'DP':
    secondaryTemp1 = 'DB'
    secondaryTemp2 = 'WB'
elif primaryTemp == 'WB':
    secondaryTemp1 = 'DB'
    secondaryTemp2 = 'DP'

# Initalize result array with heading data
resultsArray = [['Starting Year', 'Ending Year', 'Weather Station ID', '', ''],
                [start_year, end_year, location, '', ''],
                ['', '', '', '', ''],
                ['Month', 'Percentile', primaryTemp + '(F)', 'MC' + secondaryTemp1 + '(F)', 'MC' + secondaryTemp2 + '(F)']
                ]

# Write final results
# Display temperature data for each percentile for each month
print('Formatting data')
for month in range(1,13):
    # Get data for this month in all years
    monthIndex = month - 1
    thisMonthData = yearsData[monthIndex]['data']
    # Ensure month has at least 8 valid sets over all years
    if yearsData[monthIndex]['months'] < 8 :
        resultsArray.append([month, '', '', '', ''])
        continue
    # Sort month by primary index and take index for percentile
    sortedMonth = np.sort(yearsData[monthIndex]['data'], order=primaryTemp)
    ind996 = math.ceil(len(sortedMonth)*(0.004))
    ind990 = math.ceil(len(sortedMonth)*(0.01))
    ind020 = math.floor(len(sortedMonth)*(0.98))
    ind010 = math.floor(len(sortedMonth)*(0.99))
    ind004 = math.floor(len(sortedMonth)*(0.996))
    # Get temperature data at each percentile
    p996 = sortedMonth[primaryTemp][ind996]
    p990 = sortedMonth[primaryTemp][ind990]
    p020 = sortedMonth[primaryTemp][ind020]
    p010 = sortedMonth[primaryTemp][ind010]
    p004 = sortedMonth[primaryTemp][ind004]
    s1996 = sortedMonth[secondaryTemp1][ind996]
    s1990 = sortedMonth[secondaryTemp1][ind990]
    s1020 = sortedMonth[secondaryTemp1][ind020]
    s1010 = sortedMonth[secondaryTemp1][ind010]
    s1004 = sortedMonth[secondaryTemp1][ind004]
    s2996 = sortedMonth[secondaryTemp2][ind996]
    s2990 = sortedMonth[secondaryTemp2][ind990]
    s2020 = sortedMonth[secondaryTemp2][ind020]
    s2010 = sortedMonth[secondaryTemp2][ind010]
    s2004 = sortedMonth[secondaryTemp2][ind004]
    # Append percentile values to final array
    resultsArray.append([month, '99.6%', p996, s1996, s2996])
    resultsArray.append(['', '99.0%', p990, s1990, s2990])
    resultsArray.append(['', '2.0%', p020, s1020, s2020])
    resultsArray.append(['', '1.0%', p010, s1010, s2010])
    resultsArray.append(['', '0.4%', p004, s1004, s2004])
saveCSV(resultsArray,'results/final')

print("mission accomplished")