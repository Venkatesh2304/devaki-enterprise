import pandas as pd
import datetime
import json
import os
def rounds(x) :
    return round(float(x),2)
def create(df,filename) :
 col=df.columns
 inv=list(set(list(df[col[4]])))
 dicts=[]
 for i in inv :
   df1=df[df[col[4]]==i]
   df1=df1.reset_index()
   itms=[]
   sums=[sum( df1[col[25]] ) , sum( df1[col[27]] ) , sum( df1[col[28]] ) , sum( df1[col[29]] ) , sum( df1[col[30]] ),  sum( df1[col[31]] )]
   for idx,row in df1.iterrows() :
       itms.append({"productName":row[col[20]],
         "itemNo":idx+1,
         "productDesc":row[col[21]],
         "hsnCode":int(str(row[col[22]])[:4]),
         "quantity":row[col[24]],
         "qtyUnit":"PCS",
         "taxableAmount":rounds(row[col[25]]),
         "sgstRate":rounds(row[col[26]].split('+')[0]),
         "cgstRate":rounds(row[col[26]].split('+')[1]),
         "igstRate":rounds(row[col[26]].split('+')[2]),
         "cessRate":rounds(row[col[26]].split('+')[3]),
         "cessNonAdvol":0.00
         })
   row=df1.iloc[0]
   if row[col[14]]=='URP' :
       doctype='BIL'
   else :
       doctype='INV'
   dicts.append({"userGstin":row[col[7]],
               "supplyType":"O",
               "subSupplyType":1,
               "subSupplyDesc":"",
               "docType":doctype,
               "docNo":i,
               "docDate": row[col[5]].strftime('%d/%m/%Y'),
               "transType":1,
               "fromGstin":row[col[7]],
               "fromTrdName":row[col[6]],
               "fromAddr1":row[col[8]],
               "fromAddr2":row[col[9]],
               "fromPlace":row[col[10]],
               "fromPincode":int(row[col[11]]),
               "fromStateCode":33,
               "actualFromStateCode":33,
               "toGstin":row[col[14]],
               "toTrdName":row[col[13]],
               "toAddr1": row[col[15]],
               "toAddr2":row[col[16]],
               "toPlace":row[col[17]],
               "toPincode":int(row[col[11]]),
               "toStateCode":33,
               "actualToStateCode":33,
               "totalValue":round(sums[0],2),
               "cgstValue":round(sums[1],2),
               "sgstValue":round(sums[2],2),
               "igstValue":round(sums[3],2),
               "cessValue":round(sums[4],2),
               "TotNonAdvolVal":0,
               "OthValue":rounds(row[col[31]]),
               "totInvValue":rounds(row[col[32]]),
               "transMode":1,
               "transDistance":int(row[col[34]]),
               "transporterName":row[col[35]],
               "transporterId":row[col[36]],
               "transDocNo":row[col[37]],
               "transDocDate":row[col[38]].strftime('%d/%m/%Y'),
               "vehicleNo":row[col[39]],
               "vehicleType":"R",
                "itemList":itms

        })

 jsons={"version":"1.0.0621",
        "billLists":dicts}
 jsons=json.dumps(jsons)
 jsons=jsons.replace('NaN','""')
 f=open('D:\\EWAY\\'+filename+'.json','w+')
 #json=json.replace(nan,'""')
 f.write(jsons)
 f.close()               