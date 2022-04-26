import pandas as pd
import numpy as np
import datetime 
def interpret(file,date):
 df=pd.read_excel(file)
 df.drop(df.index[0:12],inplace=True)
 df.columns=df.loc[12]
 df=df.reset_index()
 df=df.drop([0])
 df=df.reset_index()
 df['Collection Code'] = df['Collection Code'].fillna(0)
 df=df.dropna(axis=0)
 df['party']=df['Party Name'].apply(lambda x: x.split('-')[0])
 df['Salesman']=df['Salesman'].apply(lambda x: x.split('-')[0])
 """dfcopy=df.copy()
 partywise={}
 for idx,row in df.iterrows() :
    try :
     partywise[row['party']]+=1
    except :
        partywise[row['party']]=1"""
 
 date=date.weekday()
 date+=1
 print(date)
 print(df)
 f=open('outstanding\\salesman.txt')
 beat=eval(f.read())
 beats={}
 for i in beat.keys() :
     beats[i.strip()] = beat[i]
 beat=beats
 f.close()
 print(beat)
 df2=[]
 df['Salesman']=df['Salesman'].apply(lambda x: x.strip())
 for idx,row in df.iterrows() :
   x=row
   u=x['Beat Name'] 
   try :
    v=beat[x['Salesman']][date]
    u=''.join(u.split(' '))
    v=[''.join(s.split(' ')) for s in v]
    if u in v  :
        #print(x['Salesman'],x['Beat Name'],date)
        df2.append(x)
   except :
      continue
 df1=pd.DataFrame(df2)
 df2=df1.copy()
 df1=df1[df1['In Days'] > 20 ]
 #df3=df1[df1['In Days']<=20]
 
 pivot=pd.pivot_table(df1,index=['Salesman','Beat Name','party'],values=['O/S Amount','In Days'],aggfunc={'O/S Amount':np.sum,'In Days':np.max},margins=True)
 pivot1=pd.pivot_table(df2,index=['Salesman','Beat Name','party'],values=['Bill Number'],aggfunc={'Bill Number':pd.Series.nunique},margins=True)
 pivot=pd.merge(pivot1,pivot,left_index=True,right_index=True)
 pivot=pivot[['Bill Number','In Days','O/S Amount']]
 print(pivot,pivot1)
 pivot.to_excel('a.xlsx')
 pivot1.to_excel('a1.xlsx')
 f=open('outstanding\\pathfile.txt')
 x=f.read()
 f.close()
 pivot.to_excel(x+'outstandingreport.xlsx')
 print('Finsihed')
 


"""pivot=pd.pivot_table(df,index=['party'],values=['O/S Amount'],aggfunc=np.sum,margins=True)
pivot=pivot[pivot['O/S Amount'] >= 100]
pivot=pivot.sort_values(by=['O/S Amount'],ascending=False)
pivot.to_excel('party.xlsx')
pivot=pd.pivot_table(df,index=['Salesman'],values=['O/S Amount'],aggfunc=np.sum,margins=True)
pivot=pivot.sort_values(by=['O/S Amount'],ascending=False)
pivot.to_excel('salesman.xlsx')"""




