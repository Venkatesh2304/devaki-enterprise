import pandas as pd
import datetime
import json
import os
def rounds(x) :
    return round(float(x),2)
import numpy as np
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def create(df,filename) :
 col=df.columns
 inv=list(set(list(df['Document Number'])))
 dicts=[]
 for i in inv :
   df1=df[df['Document Number']==i]
   df1=df1.reset_index()
   itms=[]
   def change(x) :
       try :
         return int(x)
       except :
           return x
   for idx,row in df1.iterrows() :
       itm =   {
         "SlNo":str(int(row['Sl.No.'])),
         "IsServc":"N",
         "HsnCd":row['HSN Code'].replace('.',''),
         "Qty":int(row['Quantity']),
         "Unit":"PCS",
         "UnitPrice":rounds(row['Unit Price']),
         "TotAmt":rounds(row['Gross Amount']),
         "Discount":rounds(row['Discount']),
         "AssAmt":rounds(row['Taxable Value']),
         "GstRt":rounds(row['GST Rate (%)']),
         "CgstAmt":rounds(row['Cgst Amt (Rs)']),
         "SgstAmt":rounds(row['Sgst Amt (Rs)']),
         "TotItemVal":rounds(row['Item Total']),
         }
       itms.append(itm)
   row=df1.iloc[0]
   dicts.append({
    "Version":"1.1",
    "TranDtls":{
               "TaxSch":"GST",
               "SupTyp":"B2B",
        },
    "DocDtls":{
               "Typ":"INV",
               "No":row['Document Number'],
               "Dt":row['Document Date (DD/MM/YYYY)'].strftime('%d/%m/%Y')
     },
     "SellerDtls":{
               "Gstin":"33AAPFD1365C1ZR",
               "LglNm":"DEVAKI ENTERPRISES",
               "TrdNm":None ,
               "Addr1":"F/4 , INDUSTRISAL ESTATE , ARIYAMANGALAM",
               "Addr2":None,
               "Loc":"TRICHY",
               "Pin":620010,
               "Stcd":"33",
               "Ph":None,
               "Em":None
     },
     "BuyerDtls":{
               "Gstin":row['Buyer GSTIN'],
               "LglNm":row['Buyer Legal Name'],
               "TrdNm":row['Buyer Trade Name'],
               "Pos":"33",
               "Addr1":row['Buyer Addr1'],
               "Addr2":None,
               "Loc":row['Buyer Location'],
               "Pin":row['Shipping Pin Code'] if row['Shipping Pin Code']!=0 else 620010 ,
               "Stcd":"33",
               "Ph":None,
     },
     "DispDtls":None,
     "ValDtls":{
               "AssVal":round(row['Total Taxable Value'],2),
               "CgstVal":round(row['Cgst Amt'],2),
               "SgstVal":round(row['Sgst Amt'],2),
               "Discount":round(row['Bill Discount'],2),
               "RndOffAmt":round(row['Round Off'],2),
               "OthChrg":round(row['TCS Amount'],2),
               "TotInvVal":round(row['Total Invoice Value'],2)
     },
     "EwbDtls":{
               "TransMode":"1",
               "Distance":3,
               "TransDocNo":row['Trans Doc No.'],
               "TransDocDt":row['Trans Doc Date'].strftime('%d/%m/%Y'),
               "VehNo":row['Vehicle No'],
               "VehType":"R"
     },
     "ItemList":itms })
 jsons=dicts
 jsons=json.dumps(jsons,cls=NpEncoder)
 #jsons=jsons.replace('NaN','""')
 f=open('D:\\EINV\\'+filename+'.json','w+')
 #json=json.replace(nan,'""')
 f.write(jsons)
 f.close()
 return len(dicts)
