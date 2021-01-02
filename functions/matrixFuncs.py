import csv
import numpy as np
from functions.dateFuncs import dateStringToStamp

def readcsv(filename):    
    ifile = open(filename, "rU")
    reader = csv.reader(ifile, delimiter=",")   
    a = []
    
    for rownum, row in enumerate(reader):
        a.append (row)
        rownum += 1
    
    ifile.close()
    return a

def slicer_vectorized(a,start,end):
    b = a.view((str,1)).reshape(len(a),-1)[:,start:end]
    return np.fromstring(b.tostring(),dtype=(str,end-start))

def clean_csv(data):
    # Delete unused columns
    headers = data[0]
    newlist = set([x for x in range(0, len(headers))])
    keepInds = set([headers.index('DATE'), headers.index('TMP'), headers.index('DEW')])
    headerKeepIndices = list(newlist^keepInds)
    data = np.delete(np.array(data), headerKeepIndices, axis=1) 
    # Delete bad rows 
    data = data[np.all(data != '+9999,9', axis=1)]

    # Delete header row
    data = np.delete(data, 0, axis=0)

    # Create stamp column
    np_date_stamps = np.array(list(map(dateStringToStamp, data[:,0])))
    np_DBs = np.array(list(map(lambda x: float(x[0:5])/10, data[:,1])))
    np_DPs = np.array(list(map(lambda x: float(x[0:5])/10, data[:,2])))
    #TEMP
    np_date_strings = np.array(data[:,0])

    # create the compound dtype
    dtype = np.dtype(dict(names=['stamp', 'DB', 'DP'], formats=[arr.dtype for arr in (np_date_stamps, np_DBs, np_DPs)]))
    #TEMP
    dtype2 = np.dtype(dict(names=['datestring', 'DB', 'DP'], formats=[arr.dtype for arr in (np_date_strings, np_DBs, np_DPs)]))
    # create an empty structured array
    rows = data.shape[0]
    data = np.empty((rows), dtype=dtype)
    #TEMP
    data2 = np.empty((rows), dtype=dtype2)
    
    # populate the structured array with the data from your column arrays
    data['stamp'], data['DB'], data['DP'] = np_date_stamps.T, np_DBs.T, np_DPs.T
    #TEMP
    data2['datestring'], data2['DB'], data2['DP'] = np_date_strings.T, np_DBs.T, np_DPs.T
    
    return data

def saveCSV(data, address):
    #### Save temp cleaned matrix
    with open(address +'.csv', 'w', newline='') as f:
        write = csv.writer(f) 
        write.writerows(data) 


