from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()
blobServiceClient = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING")) 
containerClient1 = blobServiceClient.get_container_client('staging-data')
containerClient2 = blobServiceClient.get_container_client('production-data')

def pushToProduction():
    blobClient1 = containerClient1.get_blob_client('transform-data.parquet')
    blobClient2 = containerClient2.get_blob_client('train-data.parquet')
    downloadStream = blobClient1.download_blob()
    blobClient2.upload_blob(downloadStream.readall(), overwrite=True)

    
    
    