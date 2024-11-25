import requests
import json
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()
blobServiceClient = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING")) 
containerClient = blobServiceClient.get_container_client('staging-data')

def fetchFromApi(startTime,endTime):
    startTimeStr = startTime.strftime("%Y-%m-%dT%H:%M:%S")
    endTimeStr = endTime.strftime("%Y-%m-%dT%H:%M:%S")
    
    params={
        "format":'geojson',
        "starttime":startTimeStr,
        "endtime":endTimeStr,
        "minmagnitude":4
    }
    response=requests.get('https://earthquake.usgs.gov/fdsnws/event/1/query',params=params)
    if response.status_code==200:
        uploadToAzure(response.json())
    else:
        print('Unable to fetch data')
        
def uploadToAzure(data):
    blobClient = containerClient.get_blob_client('temp-json')
    blobClient.upload_blob(json.dumps(data), overwrite=True)


    
