import GST.senders as senders
import pandas as pd
import GST.gstnumber as gstnumber
import numpy as np
import os
import datetime
from GST.automategst import automate
from GST import gstclean
import time
def r(x) :
    l1=[]
    for l in x :
        try :
            l1.append(round(l,2))
        except :
            l1.append(l)
    return l1
def invoicevalue(x) :
    fake={}
    for idx,row in x.iterrows() :
        fake[row['Invoice No']]=row['Invoice Value']
   
    return sum(fake.values())
def shortoutline(df,halfpath,outerpath) :
    df['tax']=df['Amount - Central Tax']*2
    shortb2b1=df[df['GSTIN of Recipient'].notna()]
    shortb2b=shortb2b1[shortb2b1['Transactions']!='SALES RETURN']
    shortb2c=df[df['GSTIN of Recipient'].isna()]
    shortcd=shortb2b1[shortb2b1['Transactions']=='SALES RETURN']
    shorthsn=df[df['Transactions']!='SALES RETURN']
    shortb2b=['B2B',invoicevalue(shortb2b),shortb2b['Taxable'].sum(),shortb2b['tax'].sum()]
    shortb2c=["B2C",invoicevalue(shortb2c),shortb2c['Taxable'].sum(),shortb2c['tax'].sum()]
    shortcd=["Credit Note",invoicevalue(shortcd),shortcd['Taxable'].sum(),shortcd['tax'].sum()]
    shorthsn=["HSN",invoicevalue(shorthsn),shorthsn['Taxable'].sum(),shorthsn['tax'].sum()]
    o=[r(shortb2b),r(shortb2c),r(shortcd),r(shorthsn)]
    f=open(outerpath+'log.txt')
    l=f.read()
    if len(eval(l)) >16 :
     g=[str(halfpath)]+ list(filter(lambda a: a!=halfpath , eval(l)[:-1]))
    else :
       g=[str(halfpath)]+ list(filter(lambda a: a!=halfpath , eval(l))) 
    f.close()
    f=open(outerpath+'log.txt','w+')
    f.write(str(g))
    f.close()
    f=open(halfpath+'short.txt','w+')
    f.write(str(o))
    f.close()
    return o
def outlineproducer(df,invalid,halfpath) :
 df['tax']=df['Amount - Central Tax']*2
 types={True:'b2b',False:'b2c'}
 df['type']=df['GSTIN of Recipient'].apply(lambda x: types[x==x] )
 #print(df)
 splitup=pd.pivot_table(df,index=['GSTIN of Recipient'],values=['Taxable','Amount - Central Tax','tax'],aggfunc=np.sum)
 #finals=[]
 #final=pd.pivot_table(df,index=['Transactions','type'],values=['Taxable','tax','Amount - Central Tax','Amount - State/UT Tax'],aggfunc=np.sum)
 #for idx,row in final.iterrows() :
 #  finals.append([idx['type'],idx['Transactions'],row['Taxable','Amount - Central Tax','tax']])
 #print(finals)
 result=pd.pivot_table(df,index=['Transactions'],values=['Taxable','tax','Amount - Central Tax','Amount - State/UT Tax'],columns=['type'],aggfunc=np.sum)
 result=result.reorder_levels([1,0], axis=1).sort_index(axis=1).reindex(['Taxable','tax','Amount - Central Tax','Amount - State/UT Tax'], level=1, axis=1)
 with pd.ExcelWriter(halfpath+'Report.xlsx') as writer:
     result.to_excel(writer, sheet_name='Summary')
     invalid.to_excel(writer, sheet_name='Invalid')
     splitup.to_excel(writer, sheet_name='splitup')
 return result
def types(x):
    if x == np.nan :
        return 'b2c'
    else :
        return 'b2b'
def checkhsn(x) :
    hsnfile=pd.read_excel(r'GST\HSN.xlsx')
    sacfile=pd.read_excel(r'GST\HSN.xlsx',sheet_name='SAC')
    hsnfile=pd.Series(list(hsnfile['HSN Code'])+list(sacfile['SAC Code']))
    hsnfile=set(list(hsnfile))
    hsnfile,x=[int(i) for i in hsnfile],[int(i) for i in x]
    return list((set(x)^set(hsnfile))&set(x))
def correct(df,invalid,pathcsv,path,halfpath,outerpath) :
    df['HSN']=df['HSN'].apply(lambda x: str(str(x).replace('.','')))
    invalidcan=invalid[invalid['name']=='Canceled']
    dfs=df.copy()
    for idx,row in invalidcan.iterrows() :
        for idx1,row1 in df.iterrows() :
            if row1['GSTIN of Recipient']==row['value'] :
                if datetime.datetime.strptime(row1['Invoice Date'],'%d/%m/%Y')>=datetime.datetime.strptime(row['details'],'%d/%m/%Y') :
                    dfs.loc[idx1,'GSTIN of Recipient']=row['change']
    df=dfs
    invalid=invalid[invalid['name']!='Canceled']
    df=df.replace(list(invalid['value']),list(invalid['change']))
    df.to_csv(pathcsv)
    os.remove(path)
def checkgst(x,df) :
    
    f=open('GST\\acc.txt')
    accgst=eval(f.read())
    f.close()
    f=open('GST\\rej.txt')
    rejgst=eval(f.read())
    f.close()
    acc,rej,check=[],[],[]
    for i in x :
        if i!=np.nan :
            if i in accgst :
                acc.append(i)
            elif i in rejgst :
                rej.append(i)
            else :
                check.append(i)
        else :
            t=0
    if check.count(np.nan) !=-1 :
        #print(check)
        try :
         check.remove(np.nan)
        except :
            check=check
    cancel,canceldate=[],[]
    if check!=[] :
     newacc,newrej,cancel,canceldate=gstnumber.result(check,df)
     acc+=newacc
     rej+=newrej
    f=open('GST\\acc.txt','w+')
    f.write(str(acc))
    f.close()
    f=open('GST\\rej.txt','w+')
    f.write(str(rej))
    f.close()
    return list(set(rej)),cancel,canceldate

def main(pathcsv,path,halfpath,outerpath) :
 start = time.time()
 df=pd.read_csv(pathcsv,dtype={'HSN':str,'Invoice Date':str})
 print("read csv" , time.time() - start )
 #rename columns if you want 
 if os.path.exists(path) :
    start1 = time.time()
    invalid=pd.read_excel(path)
    invalid=pd.read_excel(path,sheet_name='errors',dtype=str)
    correct(df,invalid,pathcsv,path,halfpath,outerpath)   
    print('correct',time.time()-start1)
 else :
    #rejgst,cancel,canceldate=checkgst(list(set(list(df['GSTIN of Recipient']))),df)
    rejgst,cancel,canceldate=[],[],[]
    start2=time.time()
    df['HSN']=df['HSN'].apply(lambda x: str(str(x).replace('.','')))
    df['lenhsn']=df['HSN'].apply(lambda x: len(str(x))==8 or len(str(x))==7 or len(str(x))==6 )
    rejhsn=list(set(list(df[df['lenhsn']==False]['HSN'])))
    acchsn=set(list(df[df['lenhsn']==True]['HSN']))
    acchsn=list(acchsn)
    ##print(acchsn)
    rejhsn+=checkhsn(acchsn)
    try :
        rejhsn.remove(np.nan)
    except :
        rejhsn=rejhsn
    try :
        rejhsn.remove('nan')
    except :
        rejhsn=rejhsn
    df['Invoice Date']=df['Invoice Date'].apply(lambda x: x.split('-')[0].zfill(2) +'-'+x.split('/')[1].zfill(2)+'-'+ x.split('/')[2])
    print('time1',time.time()-start2)
    if len(rejgst+rejhsn) != 0 or len(cancel):
     invalid=pd.DataFrame.from_dict({'name': ['GST number']*len(rejgst) + ['HSN number']*len(rejhsn) , 'value':rejgst+rejhsn , 'change':[np.nan]*len(rejhsn+rejgst),'details':''})
     if len(cancel)!=0 :
        invalid = pd.concat([invalid,pd.DataFrame.from_dict({'name':['Canceled']*len(cancel),'value':cancel,'change':[np.nan]*len(cancel),'details':canceldate})])
     invalid=invalid.reset_index()
     print('time2',time.time()-start2)
     with pd.ExcelWriter(path) as writer:
            #df.to_excel(writer, sheet_name='Summary')
            invalid.to_excel(writer, sheet_name='errors')
     print('time3',time.time()-start2)
   
     short=shortoutline(df,halfpath,outerpath)
     report=outlineproducer(df,invalid,halfpath)
     print('time4',time.time()-start2)
   
     return 0,df,invalid,report,short
    else :
      df['type']=df['GSTIN of Recipient'].apply(lambda x: types(x))
      df=df.astype({'Amount - Central Tax':float,'Taxable':float,'Amount - State/UT Tax':float,'Invoice Value':float})
      df['Amount - Central Tax']=df['Amount - Central Tax'].round(decimals = 2)
      df['Invoice Value']=df['Invoice Value'].round(decimals = 2)
      df['Amount - State/UT Tax']=df['Amount - State/UT Tax'].round(decimals = 2)
      df['Taxable']=df['Taxable'].round(decimals = 2)
      report=outlineproducer(df,pd.DataFrame(),halfpath)
      short=shortoutline(df,halfpath,outerpath)
      month=halfpath.split('\\')[-2]
      senders.get(df,month)
      print('time 2 ',time.time()-start)
      return 1,df,1,report,short
    
def comp(pathcsv,halfpath) :
      df=pd.read_csv(pathcsv,dtype={'HSN':str,'Invoice Date':str})
      print(df['HSN'])
      df['HSN']=df['HSN'].apply(lambda x: str(str(x).replace('.','')))
      df['type']=df['GSTIN of Recipient'].apply(lambda x: types(x))
      df=df.astype({'Amount - Central Tax':float,'Taxable':float,'Amount - State/UT Tax':float,'Invoice Value':float})
      df['Amount - Central Tax']=df['Amount - Central Tax'].round(decimals = 2)
      df['Invoice Value']=df['Invoice Value'].round(decimals = 2)
      df['Amount - State/UT Tax']=df['Amount - State/UT Tax'].round(decimals = 2)
      df['Taxable']=df['Taxable'].round(decimals = 2)
      month=halfpath.split('\\')[-2]
      senders.get(df,month)
      return True 
    

    
   
