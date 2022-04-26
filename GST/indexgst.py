from flask import Flask,render_template,request,redirect,send_file
from datetime import datetime
import os
from GST.automategst import automate
from GST import gstmain
import pandas as pd
import numpy as np
from GST.gstclean import clean
import calendar
app = Flask(__name__)
def create(month1,year1) :
    global halfpath
    global outerpath
    global path
    global pathcsv
    halfpath='C:\\Users\\'+desktopuser+'\Desktop\GST\\'+month1+'-'+year1+'\\'
    outerpath='C:\\Users\\'+desktopuser+'\Desktop\GST\\'
    pathx=outerpath+list(automate(month1+'-'+year1,outerpath))[0]
    os.makedirs(halfpath)
    df=pd.read_csv(pathx,dtype={'HSN':str,'Outlet Code':str })
    pathcsv=halfpath+month1+'-'+year1+'.csv'
    path=halfpath+'Error Report.xlsx'
    df=clean(df)
    df.to_csv(pathcsv)
    return errsuccess()
@app.route('/gst/errsuccess',methods=['GET','POST'])
def errsuccess() :
    global path
    global pathcsv
    global halfpath
    global outerpath
    try :
     os.remove(path)
    except:
      gg=0
    err,df,inv,rep,short=gstmain.main(pathcsv,path,halfpath,outerpath)
    s=[]
    if err==0 :
         for idx,row in inv.iterrows() :
             s.append([row['name'],row['value'],row['change'],row['details'],str(idx)])
         return render_template("GST\\error.html",s=s)
    else :
        return render_template("success.html",short=short)
@app.route('/gst/correction', methods = ['GET', 'POST'])
def correction() :
   global path
   global pathcsv
   global halfpath
   global outerpath
   df=pd.read_csv(pathcsv,dtype={'HSN':str,'Invoice Date':str})
   inv=pd.read_excel(path,sheet_name='errors',dtype=str)
   if request.method=='POST' :
    mode=request.form['mode']
    if mode=='Online' :
       for i in inv.index :
           inv.loc[i,'change']=str(request.form[str(i)])
       with pd.ExcelWriter(path) as writer:
            df.to_excel(writer, sheet_name='Summary')
            inv.to_excel(writer, sheet_name='errors')      
    inv1=pd.read_excel(path,sheet_name='errors',dtype=str)
    #print(inv1)
    gstmain.correct(df,inv1,pathcsv,path,halfpath,outerpath)
    return errsuccess()
@app.route('/gst/download',methods=['GET',"POST"])
def  download() :
    global halfpath
    try :
     return send_file(halfpath+'gst.json',as_attachment=True)
    except :
        return "<p> Go to Desktop >> GST >> MONTH-YEAR>> gst.json</p>"
@app.route('/gst/dels', methods = ['GET', 'POST'])
def dels() :
    month1=request.form['month']
    year1=request.form['year']
    os.rmdir('C:\\Users\\'+desktopuser+'\Desktop\GST\\'+month1+'-'+year1+'\\')
    create(month1,year1)
@app.route('/gst/view/<month>/<year>',methods = ['GET', 'POST'])
def view(month,year) :
    global path
    global pathcsv
    global outerpath
    global halfpath
    halfpath='C:\\Users\\'+desktopuser+'\Desktop\GST\\'+month+'-'+year+'\\'
    outerpath='C:\\Users\\'+desktopuser+'\Desktop\GST\\'
    pathcsv=halfpath+month+'-'+year+'.csv'
    path=halfpath+'Error Report.xlsx'
    df=pd.read_csv(pathcsv)
    short=gstmain.shortoutline(df,halfpath,outerpath)
    if os.path.exists(path) :
        alreadyerr=1
        return render_template('GST\\view.html',month=month,year=year,short=short,alreadyerr=alreadyerr)
    else:
        return render_template('GST\\view.html',month=month,year=year,short=short,pathjson=halfpath+'gst.json')
@app.route('/gst/alreadyexist', methods = ['GET', 'POST'])    
def gets() :
   if request.method == 'POST':
    month1=request.form['month']
    month1=str(int(month1))
    year1=request.form['year']
    if os.path.exists('C:\\Users\\'+desktopuser+'\Desktop\GST\\'+month1+'-'+year1+'\\') :
     return redirect('/gst/view/'+month1+'/'+year1)
    else :
     return create(month1,year1)
@app.route('/gst',methods=['POST','GET'])
def index():
   date=datetime.now()
   month=str(date.month)
   year=str(date.year)
   f=open('C:\\Users\\'+desktopuser+'\Desktop\GST\log.txt')
   months= eval(f.read())
   f.close()
   shorts={}
   months1=[]
   names={}
   for i in months :
       f=open(str(i)+'short.txt')
       shorts[i.split("\\")[-2]]=eval(f.read())
       f.close()
   months1=[k.split("\\")[-2] for k in months]
   for i in months1 :
       names[i]=calendar.month_name[int(i.split('-')[0])]+ ' , ' + i.split('-')[1]
   return render_template('GST\\index.html',months=months1,shorts=shorts,names=names)
if __name__ == '__main__':
   app.run()
   f=open('GST\\gst.txt')
   desktopuser=eval(f.read())['desktopuser']
   f.close()

def main() :
    app.run()
