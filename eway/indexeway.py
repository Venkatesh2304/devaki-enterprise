import pandas as pd
import numpy as np
from selenium import webdriver
from flask import Flask,render_template,request,redirect,send_file
import os
from EWAY.automateeway import automate
from EWAY.processeway import process
import datetime
import win32com.client
from win32com.client import Dispatch
def macroseway(filename) :
 xl = win32com.client.Dispatch('Excel.Application')
 wb = xl.Workbooks.Open(filename)
 writeData = wb.Worksheets('Main')
 writeData.Cells(13,5).Value = filename
 xl.visible =True
 
xl = None
app = Flask(__name__)
@app.route('/eway/save',methods=['POST','GET'])
def saveeway() :
         x=request.form
         data={}
         for key in x.keys() :
           if key!='vehicle'  :
             data[key]=x[key]
         f=open('log.txt','w')
         f.write(str(data))
         f.close()
         return redirect('/eway')
@app.route('/eway/generate',methods=['POST','GET'])
def generateeway() :
         x=request.form
         data={}
         for key in x.keys() :
           if key!='vehicle' and key!='date':
             data[key]=x[key]
         f=open('log.txt','w')
         f.write(str({}))
         f.close()
         date=x['date'].split('-')[2]+'/'+x['date'].split('-')[1]+'/'+x['date'].split('-')[0]
         files=automate(data,date)
         total=[]
         error=[]
         for i in files.keys() :
            if files[i]!= 0:
             df=pd.read_excel(files[i])
             total.append(df)
            else :
                error.append(i)
         if error!=[] :
            return render_template('ewayerror.html',error=error)
         df=pd.concat(total)
         df=process(df,data)
         filename=x['date']
         filename.replace('-','.')
         if not os.path.exists(r'D:\EWAY\\'+filename+'.xlsx') :
           df.to_excel(r'D:\EWAY\\'+filename+'.xlsx',index=False)
         else :
             df=pd.concat([df,pd.read_excel(r'D:\EWAY\\'+filename+'.xlsx')])
             df.to_excel(r'D:\EWAY\\'+filename+'.xlsx',index=False)
         macros(filename)
         return redirect('/eway')
@app.route('/eway')
def indexeway():
   f=open('log.txt')
   prev=eval(f.read())
   f.close()
   prev1=[]
   l=0
   for i in prev.keys() :
     if i!='date' :
       prev1.append([i,prev[i]])
     else :
         prevdate=prev[i]
         l=1
   if l==0 :
       currentdate=datetime.datetime.now()
       previousdate=currentdate - timedelta(days = 1)
       if datetime.datetime.now().hours > 15 :
         prevdate=currentdate.strftime('%Y-%m-%d')
       else :
           prevdate=previousdate.strftime('%Y-%m-%d')
   return render_template('ewayindex.html',prev=prev1,prevdate=prevdate)


x=0
if __name__ == '__main__':
   app.run()
   
