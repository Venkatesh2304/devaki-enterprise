from pickle import TRUE
from flask import *
import pandas as pd 
from selenium import webdriver 
from datetime import datetime 
from datetime import timedelta
import outstanding 
import creditlock 
from eway.EGenerate import EGenerate
import eway.esync as esync
import os 
import shutil
import chromedriver_autoinstaller
import webbrowser


app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"

@app.route("/") 
def render_home() :
    return render_template("index.html")
@app.route("/config") 
def render_configuration() : 
    with open("config.txt") as f : 
        return render_template("config.html" , config =  eval(f.read()) )
@app.route("/setconfig",methods=["POST"])
def setconfiguration() :
      req = request.form
      with open("config.txt") as f : 
          config = eval(f.read())
      for key , value in req.items() :
           if type(config[key]) == int :
               value = int(value)
           config[key] = value 
      with open("config.txt","w+") as f :
          f.write(str(config))
      return render_configuration()
@app.route("/update")
def update_chromedriver() :
    shutil.copy( chromedriver_autoinstaller.install(path= "D:\\") , r'chromedriver.exe')
    return "Finished Update"

@app.route("/outstanding")
def render_outstanding() : 
    return render_template("outstanding.html")
@app.route("/outstanding/<date>/<randomkey>") 
def Outstanding(date,randomkey) : #date format in y-m-
    if date == "today" :
        date = datetime.now().strftime("%Y-%m-%d")
    else : 
        date = datetime.strptime(date,"%Y-%m-%d")
    outstanding.main(date = date,days = 20) 
    return send_file("outstandingreport.xlsx",as_attachment=True)

@app.route("/creditlock")
def Creditlock() : 
    creditlock.main()
    return {"status" : 1}

@app.route('/eway')
def render_eway():
   beats=pd.read_excel('beat.xlsx')
   beats=list(set(list(beats['Beat'])))
   with open('eway\\vehicle.txt') as f : 
    vehname=eval(f.read())
   vehicle = {vehname[i] : i for i in vehname.keys()}
   date = datetime.now().strftime("%Y-%m-%d")
   return render_template('ewayindex.html',beats=beats,vehicle=vehicle,date=date)
@app.route('/eway/generate',methods=['POST','GET'])
def generateeway() :
         x = request.form
         data={}
         for key in x.keys() :
           if key not in ['vehicle','date1','date2','type'] :
             data[key]=x[key]
         types = x["type"]
         date1=x['date1'].split('-')[2]+'/'+x['date1'].split('-')[1]+'/'+x['date1'].split('-')[0]
         if x['date2']!='' :
              date2=x['date2'].split('-')[2]+'/'+x['date2'].split('-')[1]+'/'+x['date2'].split('-')[0]
         else :
              date2=date1
         response = EGenerate(types, date1 , date2 ,data )
         if response is None :
             return  redirect("/eway")
         return send_file(response["fpath"],as_attachment=True)

@app.route("/esync")
def einv_sync() :
    response = esync.sync()
    return render_template("esync.html",response = response)
webbrowser.open('http://127.0.0.1:1000/')
app.run(threaded=True,debug=False,port=1000)
