from flask import Flask,render_template,request,redirect,send_file,render_template_string
from datetime import datetime,timedelta,date
import os
import pandas as pd
import numpy as np
import openpyxl
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
import webbrowser
import pickle
from selenium import webdriver
from calendar import month_name
from win32com.client import Dispatch
from pythoncom import CoInitialize
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dateutil.rrule import rrule, MONTHLY
import time
import threading
import shutil

from eway.EGenerate import EGenerate
from credit.automatecredit import main as credit
from outstanding.main import outstanding
from credit.removelock import main as removelock


app = Flask(__name__)
@app.route('/removelock')
def removelocks():
    removelock()

@app.route('/credit',methods=['POST','GET'])
def credits() :
    credit()
@app.route('/outstanding/download/<date>',methods=['POST','GET'])
def outstandingdownload(date) :
    global useraccess
    if useraccess['outstanding']==False :
       return render_template('pricing.html',err='outstanding',useraccess=useraccess)
    return send_file(r'outstanding\outstandingreport.xlsx',as_attachment=True)
@app.route('/outstanding/<date>',methods=['POST','GET'])
def getoutstanding(date) :
    global useraccess
    if useraccess['outstanding']==False :
       return render_template('pricing.html',err='outstanding',useraccess=useraccess)
    if date!='today' :
      outstanding(20,date)
    else :
      outstanding(20)
      date=datetime.now().strftime('%Y-%m-%d')
    f=open('cache.txt')
    f1=eval(f.read())
    f.close()
    f=open('cache.txt','w+')
    date=date.split('-')[2]+'/'+date.split('-')[1]+'/'+date.split('-')[0]
    f1['outstanding']=date 
    f.write(str(f1))
    f.close()
    return send_file(r'outstanding\outstandingreport.xlsx',as_attachment=True)
@app.route('/outstanding',methods=['POST','GET'])
def outstandingdate() :
    global useraccess
    if useraccess['outstanding']==False :
       return render_template('pricing.html',err='outstanding',useraccess=useraccess)
    f=open('cache.txt')
    f1=eval(f.read())
    f.close()
    return render_template('outstanding.html',last=f1['outstanding'])

@app.route('/download/<filename>',methods=['POST','GET'])
def download(filename) :
    return send_file(filename.replace('..','\\'),as_attachment=True)




#eway adn einvoice 
@app.route('/eway/generate',methods=['POST','GET'])
def generateeway() :
         x=request.form
         data={}
         for key in x.keys() :
           if key not in ['vehicle','date1','date2','type'] :
             data[key]=x[key]
         types = x['type']
         date1=x['date1'].split('-')[2]+'/'+x['date1'].split('-')[1]+'/'+x['date1'].split('-')[0]
         if x['date2']!='' :
              date2=x['date2'].split('-')[2]+'/'+x['date2'].split('-')[1]+'/'+x['date2'].split('-')[0]
         else :
              date2=date1
         EGenerate(types , date1 , date2 ,data ) 
         return "<p>Success</p>"

@app.route('/eway')
def indexeway():
   global useraccess   
   f=open('eway\\log.txt')
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
       currentdate=datetime.now()
       previousdate=currentdate - timedelta(days = 1)
       if datetime.now().hour > 15 :
         prevdate=currentdate.strftime('%Y-%m-%d')
       else :
           prevdate=previousdate.strftime('%Y-%m-%d')
   beats=pd.read_excel('beat.xlsx')
   beats=list(set(list(beats['Beat'])))
   f=open('cache.txt')
   cached=eval(f.read())['eway']
   mini=cached[1]
   maxi=cached[2]
   f=open('eway\\vehicle.txt')
   vehname=eval(f.read())
   f.close()
   vehicle={}
   for i in vehname.keys() :
     vehicle[vehname[i]]=i
   return render_template('ewayindex.html',prev=prev1,prevdate=prevdate,beats=beats,mini=mini,maxi=maxi,vehicle=vehicle)

@app.route('/home')
def home() :
    global userdata
    return render_template('index.html')
status=''
cred = credentials.Certificate(r"firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
f=open('config.bin','rb')
userdata=pickle.load(f)
f.close()
doc_ref = db.collection(u'user').document(userdata['user'])
doc = doc_ref.get()
if doc.exists:
    webbrowser.open('http://localhost:1000/home')
    app.run(host='localhost',port='1000',threaded=True)
else:
    sys.exit()



