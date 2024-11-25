from sklearn.preprocessing import MinMaxScaler,OneHotEncoder
import pandas as pd
from io import BytesIO
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()
blobServiceClient = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING")) 
containerClient = blobServiceClient.get_container_client('staging-data')

def downloadParquetFromAzure():
    blobClient = containerClient.get_blob_client('cleaned-data.parquet')
    downloadedBlob = blobClient.download_blob()
    data = downloadedBlob.readall()
    dF = pd.read_parquet(BytesIO(data))
    transformData(dF)

def transformData(dF):
    if dF.empty:
        print("DataFrame is empty. Returning empty results.")
        return 0  # Returning 0 to indicate empty DataFrame
    
    def magCategory(mag):
        if mag>=7:
            return 'Major'
        elif mag>=6:
            return 'Strong'
        elif mag>=5:
            return 'Moderate'
        else:
            return 'Light'
        
    dF['magCategory']=dF['mag'].apply(magCategory)
    
    numColumns=['tsunami','mag','sig','nst','dmin','gap']
    catColumns=['place','magType','magCategory']
    
    scaler=MinMaxScaler()
    dF[numColumns]=scaler.fit_transform(dF[numColumns])
    
    dFCategory = dF[catColumns]
    dF = dF.drop(columns=catColumns)
        
    encoder=OneHotEncoder(handle_unknown='ignore',sparse_output=False)
    encodeData = encoder.fit_transform(dFCategory) 
    encodedDF = pd.DataFrame(encodeData,columns=encoder.get_feature_names_out(catColumns))
    dF = pd.concat([dF, encodedDF], axis=1)
    uploadParquetToAzure(dF)
    return 1 # Returning 1 to indicate successful transformation
    
def uploadParquetToAzure(dataFrame):
    blobClient = containerClient.get_blob_client('transform-data.parquet')    
    parquetBuffer = BytesIO()
    dataFrame.to_parquet(parquetBuffer, index=False)
    parquetBuffer.seek(0)
    blobClient.upload_blob(parquetBuffer, overwrite=True)