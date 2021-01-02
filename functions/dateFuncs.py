from datetime import datetime, timedelta

def dateStringToStamp(dateString):
    dtObj = datetime.fromisoformat(dateString)
    timestamp = (dtObj - datetime(1970, 1, 1)) / timedelta(seconds=1)
    return timestamp

def stampToString(stamp):
    dtObj = datetime.utcfromtimestamp(stamp)
    return dtObj.strftime("%Y-%m-%d  %H:%M:%S")

def stampToMonth(stamp):
    dtObj = datetime.utcfromtimestamp(stamp)
    return dtObj.month

def stampToHour(stamp):
    dtObj = datetime.utcfromtimestamp(stamp)
    return dtObj.hour