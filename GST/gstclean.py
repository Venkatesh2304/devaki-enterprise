import pandas as pd
import numpy as np
from GST import opengrand
def change(x) :
    if x!=x :
        return np.nan
    else :
        
        return str(x).split('-')[1]
           
def clean(df) :
 #df=pd.read_csv(pathcsv,dtype={'HSN':str,'Outlet Code':str  })
 ds=df.copy()
 df1=df[df['Outlet Code'].isna()]
 df=df[df['Outlet Code'].notna()]
 df['Outlet Code']=df['Outlet Code'].apply(lambda x:change(x) )
 gst={}
 for i in set(list(df['Outlet Code'])) :
     gst[i]=np.nan
 invalid={}
 for idx,row in df.iterrows() :
     if row['GSTIN of Recipient'] == row['GSTIN of Recipient'] :
         if gst[row['Outlet Code']]==row['GSTIN of Recipient'] or gst[row['Outlet Code']]!= gst[row['Outlet Code']]:
                gst[row['Outlet Code']]=row['GSTIN of Recipient']
 df['GSTIN of Recipient']=df['Outlet Code'].apply(lambda x:gst[x])
 df2=pd.concat([df,df1])
 return df2
