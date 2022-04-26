from flask import Flask,render_template,request,redirect,send_file
from os import remove
from time import sleep
import sys
import os
import webbrowser
import pandas as pd
import dummybills 
app = Flask(__name__)
@app.route('/generatedummy',methods=['POST'])
def generatedummy() :
    data=request.form
    finalprod=[]
    for i in data.keys() :
        if i=='beat' :
            beat=data[i]
            continue
        for j in prod :
         if j[0].strip() == i.strip() :
          finalprod.append([j[0].strip(),int(data[i]),j[1],j[2]])
          break
    #print(finalprod)
    dummybills.main([beats[beat],beat,finalprod,blockedshops])
    return "<p> a<p>"     
@app.route('/dummybills')
def index() :
    prods=[]
    for i in prod :
      prods.append(i[0])
    return render_template('indexdummybills.html',prods=prods,beat=beats.keys())
beats={}
prod=[]
df=pd.read_excel('dummybills\\inputdummy.xlsx',sheet_name='product')
for idx,row in df.iterrows() :
    print(row)
    prod.append([row['product'],row['mrp'],row['minimum']])
df=pd.read_excel('inputdummy.xlsx',sheet_name='beats')
for idx,row in df.iterrows() :
    beats[row['beat']] = row['salesman']
df=pd.read_excel('inputdummy.xlsx',sheet_name='blocked')
blockedshops=list(df['blocked'])
webbrowser.open('http://127.0.0.1:5000/dummybills')
app.run()
