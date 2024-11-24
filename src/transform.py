import pandas as pd

def transformData(dataFrame):
    
    def magCategory(mag):
        if mag>=7:
            return 'Major'
        elif mag>=6:
            return 'Strong'
        elif mag>=5:
            return 'Moderate'
        else:
            return 'Light'
        
    dataFrame['magCategory']=dataFrame['mag'].apply(magCategory)