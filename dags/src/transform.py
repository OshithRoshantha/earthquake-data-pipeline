from sklearn.preprocessing import MinMaxScaler,OneHotEncoder
import pandas as pd

def transformData(dF,scaler,encoder):
    
    if dF.empty:
        print("DataFrame is empty. Returning empty results.")
        return pd.DataFrame(), scaler, encoder
    
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
    
    if scaler is 0:
        scaler=MinMaxScaler()
        dF[numColumns]=scaler.fit_transform(dF[numColumns])
    else:
        dF[numColumns]=scaler.transform(dF[numColumns])
        
    if encoder is 0:
        encoder=OneHotEncoder(handle_unknown='ignore',sparse_output=False)
        encodeData=encoder.fit_transform(dF[catColumns])  
    else:
        encodeData=encoder.transform(dF[catColumns])
    
    return encodeData,scaler,encoder