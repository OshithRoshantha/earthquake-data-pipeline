import pandas as pd

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
    return dFrame