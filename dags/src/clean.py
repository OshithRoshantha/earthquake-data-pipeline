import pandas as pd
import json
from io import BytesIO
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()
blobServiceClient = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING")) 
containerClient = blobServiceClient.get_container_client('staging-data')

def fetchFromAzure():
    blobClient = containerClient.get_blob_client('temp-json')
    blobData = blobClient.download_blob()
    data = json.loads(blobData.readall())
    preProcessing(data)
    
def uploadParquetToAzure(dataFrame):
    blobClient = containerClient.get_blob_client('cleaned-data.parquet')
    existingParquet = False
    try:
        existing_blob = blobClient.download_blob()
        existingParquet = True
    except Exception as e:
        existingParquet = False
        
    if existingParquet:
        existingData = existing_blob.readall()
        existingDf = pd.read_parquet(BytesIO(existingData))
        updatedDf = pd.concat([existingDf, dataFrame], ignore_index=True)
    else:
        updatedDf = dataFrame
        
    parquetBuffer = BytesIO()
    updatedDf.to_parquet(parquetBuffer, index=False)
    parquetBuffer.seek(0)
    blobClient.upload_blob(parquetBuffer, overwrite=True)  
    
def preProcessing(rawData):
    features=rawData.get('features',[])
    processedData=[]
    
    for feature in features:
        prop=feature.get('properties',{})
        geom=feature.get('geometry',{})
        
        earthqData={
            "id":feature.get('id',None),
            "place":prop.get('place',None),
            "time":pd.to_datetime(prop.get("time",None),unit='ms',errors='coerce'),
            "tsunami":prop.get('tsunami',None),
            "mag":prop.get('mag',None),
            "sig":prop.get('sig',None),
            "nst":prop.get('nst',None),
            "dmin":prop.get('dmin',None),
            "gap":prop.get('gap',None),
            "magType":prop.get('magType',None),
            "long":geom.get("coordinates",[None, None, None])[0],
            "lat":geom.get("coordinates",[None, None, None])[1],
            "depth":geom.get("coordinates",[None, None, None])[2],
        }
        
        processedData.append(earthqData)
        
    dFrame=pd.DataFrame(processedData)
    dFrame=dFrame.dropna()
    uploadParquetToAzure(dFrame)
    return dFrame