from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import os
import pandas as pd
import json

load_dotenv()

def pushToAzure(dataFrame):
    
    credential=DefaultAzureCredential()
    accountName=os.getenv('AZURE_ACCOUNT_NAME')
    blobServiceClient=BlobServiceClient(account_url=f"https://{accountName}.blob.core.windows.net", credential=credential)
    containerClient=blobServiceClient.get_container_client('ml-datasets')
    blobClient=containerClient.get_blob_client('data.json')
    
    try:
        existingBlob=blobClient.download_blob().readall()
        existingData=json.loads(existingBlob)
        existingDf=pd.json_normalize(existingData)
    except:
        existingDf=pd.DataFrame()
        
    combinedDf=pd.concat([existingDf, dataFrame], ignore_index=True)
    uniqueDf=combinedDf.drop_duplicates(subset=['id'], keep='last')
    uniqueJsonData=uniqueDf.to_json(orient='records', lines=True)
    blobClient.upload_blob(uniqueJsonData, overwrite=True)
    
    
    
    