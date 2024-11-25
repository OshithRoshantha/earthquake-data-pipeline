from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from io import BytesIO
import pandas as pd
import os

load_dotenv()
blobServiceClient = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING")) 
containerClient1 = blobServiceClient.get_container_client('staging-data')
containerClient2 = blobServiceClient.get_container_client('production-data')

def pushToProduction():
    blobClient1 = containerClient1.get_blob_client('transform-data.parquet')
    blobClient2 = containerClient2.get_blob_client('train-data.parquet')
    blobClient3 = containerClient2.get_blob_client('train-data.csv')
    downloadStream = blobClient1.download_blob()
    parquetData = downloadStream.readall()
    blobClient2.upload_blob(parquetData, overwrite=True)
    
    parquet_df = pd.read_parquet(BytesIO(parquetData))
    csv_data = parquet_df.to_csv(index=False)
    blobClient3.upload_blob(csv_data, overwrite=True)
    
    
    