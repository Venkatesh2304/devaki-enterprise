import pandas as pd
import numpy as np
from GST import gstnumber
from GST import senders
def outlineproducer(df,invalid) :
 
 dfjs=df.copy()
 result=pd.pivot_table(df,index=['Transactions'],values=['Taxable','tax','Amount - Central Tax','Amount - State/UT Tax'],columns=['type'],aggfunc=np.sum)
 result=result.reorder_levels([1,0], axis=1).sort_index(axis=1).reindex(['Taxable','tax','Amount - Central Tax','Amount - State/UT Tax'], level=1, axis=1)
##print(result)
 with pd.ExcelWriter('result.xlsx') as writer:
     result.to_excel(writer, sheet_name='Summary')
     invalid.to_excel(writer, sheet_name='Invalid')
 return invalid,result,dfjs

def change(x) :
    if pd.isna(x) :
        return 'b2c'
    else :
        return 'b2b'
def main(path,validity,hsn):
 df=pd.read_csv(path)
 if validity == True :
  acc,rej,check=[],[],[]
  try:
   f1=open('acc.txt','r')
   prevacc=eval(f1.read())
   f1.close()
  except :
     prevacc=[]
  try:
   f1=open('rej.txt','r')
   prevrej=eval(f1.read())
   f1.close()
  except :
     prevrej=[]
  t=set(list(df['GSTIN of Recipient']))
  for i in t :
   if i==i :
    if i in prevacc :
        acc.append(i)
    elif i in prevrej :
        rej.append(i)
    else :
        #print(i,prevrej,check)
        check.append(i)
  #print(prevacc)
  #print(check,rej)
  if check!=[] :
   newacc,newrej=gstnumber.result(check)
   acc+=newacc
   rej+=newrej
  f1=open('acc.txt','w+')
  f2=open('rej.txt','w+')
  f1.write(str(acc))
  f2.write(str(rej))
  f1.close()
  f2.close()
#
  df['validity']=df['GSTIN of Recipient'].apply(lambda x: (x in acc) or (x!=x) )
 else :
     df['validity']=True
# validity of hsn 
 t=df['GSTIN of Recipient']     
 df['type']=t.apply(lambda x: change(x))
 invalid=df[df['validity']==False]
 df=df[df['validity']==True]
#
 df['tax']=df['Amount - Central Tax']+df['Amount - State/UT Tax']
 return outlineproducer(df,invalid)

 #senders.get(dfjs)
