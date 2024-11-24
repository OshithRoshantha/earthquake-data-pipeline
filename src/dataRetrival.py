import requests
from datetime import datetime,timedelta

def fetchFromApi(startTime,endTime):
    params={
        "format":'geojson',
        "starttime":startTime,
        "endtime":endTime,
        "minmagnitude":4
    }
    response=requests.get('https://earthquake.usgs.gov/fdsnws/event/1/query',params=params)
    if response.status_code==200:
        return response.json()
    else:
        print('Unable to fetch data')
        
def setTime():
    executeTime=datetime.now()
    startTime=executeTime-timedelta(hours=1)
    return startTime.strftime('%Y-%m-%dT%H:%M:%S'),executeTime.strftime('%Y-%m-%dT%H:%M:%S')
    
