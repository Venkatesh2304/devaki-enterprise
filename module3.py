import pandas as pd
import  os
path = 'D:\\tax\\'
files = os.listdir(path)
out=[]
for i in files :
 try :
  df = pd.read_excel(path+i)
  date = df.iloc[6][df.columns[2]]
  last = df.iloc[-1][df.columns[-2]]
  out.append([date,last])
  print(date,last)
 except :
     print(file,'except')
pd.DataFrame(out).to_csv('tax2020-2021.csv')
