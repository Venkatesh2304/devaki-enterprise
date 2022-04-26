import pandas as pd
import GST.jsonb2b as jsonb2b
import GST.jsoncd as jsoncd
import numpy as np
from GST.prepdoc import main
def b2csub1(x) :
  print(x)
  if x['Transactions']=='SALES RETURN' : 
     return -x['Taxable']
  else :
     return x['Taxable']
def b2csub2(x) :
  if x['Transactions']=='SALES RETURN' : 
     return -x['Amount - Central Tax']
  else :
     return x['Amount - Central Tax']
def get(df,month) :
  #print(2)
  #clean 
  #df['GSTIN of Recipient']=df['GSTIN of Recipient'].apply(lambda x:x.strip())
  df=df.round(2)
  #df=df.astype({'Tax - Central Tax':int})
  df1=df[df['GSTIN of Recipient'].isna()]
  df2=df[df['GSTIN of Recipient'].notna()]
  #print(month)
  f=open('GST\\gst.txt')
  gst=eval(f.read())
  output={"gstin":gst['gstnumber'],"fp":month.split('-')[0].zfill(2) + month.split('-')[1]}
  output["version"]=gst['version']
  output["hash"]="hash"
  output['b2b']=jsonb2b.jsonconverter(df2[df2['Transactions']!='SALES RETURN'])
  #print(output)
  output['cdnr']=jsoncd.jsonconverter(df2[df2['Transactions']=='SALES RETURN'])
  #df1['Taxable'] = df1.apply(lambda x : b2csub1(x))
  #df1['Amount - Central Tax']= df1.apply(lambda x : b2csub2(x))
  dfdup1=df1[df1['Transactions']=='SALES RETURN']
  dfdup1['Taxable'] = -dfdup1['Taxable']
  dfdup1['Amount - Central Tax'] = -dfdup1['Amount - Central Tax']
  dfdup2=df1[df1['Transactions']!='SALES RETURN']
  df1=pd.concat([dfdup1,dfdup2])
  result=pd.pivot_table(df1,index=['Tax - Central Tax'],values=['Taxable','Amount - Central Tax'],aggfunc=np.sum)
  out1=[]
  result=result.round(2)
  for idx,row in result.iterrows() :
      out={}
      out['sply_ty'],out['txamt'],out['typ'],out['pos'],out['rt'],out['iamt'],out['camt'],out['samt'],out['csamt']='INTRA',row['Taxable'],'OE','33',2*idx,0,row['Amount - Central Tax'],row['Amount - Central Tax'],0
      out1.append(out)
  output['b2cs']=out1
  dfdup1=df[df['Transactions']=='SALES RETURN']
  dfdup1['Taxable'] = -dfdup1['Taxable']
  dfdup1['Amount - Central Tax'] = -dfdup1['Amount - Central Tax']
  dfdup2=df[df['Transactions']!='SALES RETURN']
  df1=pd.concat([dfdup1,dfdup2])
  hsndict={}
  for idx,row in df1.iterrows():
   if row['UOM']==row['UOM']:
    hsndict[row['HSN']]=[row['Tax - Central Tax']*2 ,row['UOM'],row['HSN Description']]
   else :
     hsndict[row['HSN']]=[row['Tax - Central Tax']*2 ,'na',row['HSN Description']]
  result=pd.pivot_table(df1,index=['HSN'],values=['Taxable','Amount - Central Tax','Total Quantity'],aggfunc=np.sum)
  t=0
  out1=[]
  result=result.astype({'Total Quantity':int})
  result=result.round({'Amount - Central Tax':2,'Taxable':2})
  for idx,row in result.iterrows() :
      t=t+1
      out={}
      out['num'],out['hsn_sc'],out['desc'],out['uqc'],out['qty'],out['txamt'],out['iamt'],out['camt'],out['samt'],out['csamt'],out['rt']=t,idx,hsndict[idx][2],hsndict[idx][1],int(row['Total Quantity']),row['Taxable'],0,row['Amount - Central Tax'],row['Amount - Central Tax'],0,hsndict[idx][0]
      out1.append(out)
  output['hsn']={'data':out1}
  output["doc_issue"]=main(df)
  #print(2)
  #month=str(int(month.split('-')[0]))+'-'+month.split('-')[1]
  f=open(r'GST\\gst.txt')
  gst=eval(f.read())
  f.close()
  f=open('C:\\Users\\'+gst['desktopuser']+'\\Desktop\\GST\\' +month+'\gst.json','w')
  print(f)
  x=str(output)
  #print(x)
  x=x.replace('nan','')
  x=x.replace('/','-')
  x=x.replace("'",'"')
  x=x.replace('cin','ctin')
  x=x.replace('txamt','txval')
  f.write(x)
  f.close()
  #f=open('C:\\Users\\new2018\\Desktop\\GST\\' +month+'\gst.json')
  #print(f.read())
  #f.close()
  #print('ok')
  #f=open(r'C:\Users\new2018\Desktop\GST\\5-2021\\gst.json','w+')
    
    
