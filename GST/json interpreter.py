import json
import pandas as pd

f=open('C:\\TC\\gst2.json')
d=json.loads(f.read())
d=d['b2b']

x1,x2,x3=[],[],[]
for i in d :
    for j in i['inv'] :
       x1.append(i['ctin'])
       x2.append(j['inum'])
       x3.append(j['val'])
df=pd.DataFrame.from_dict({'a':x1,'b':x2,'c':x3})
df.to_excel('C:\\TC\\gst2.xlsx')
f.close()
