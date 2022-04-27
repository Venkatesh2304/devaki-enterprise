from flask import Flask,render_template,request,redirect,send_file,render_template_string
from datetime import datetime,timedelta,date
import os
import creditresolve 
#from GST.automategst import automate as automategst
#from GST import gstmain
import pandas as pd
import Shogun 
import numpy as np
import openpyxl
import json
import extrabill.dummybills as dummybills
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
import webbrowser
from eway.ewaysite import ewaysite
from eway.einvsite import einvsite
import pickle
#from GST.gstclean import clean
from calendar import month_name
import eway.json as ewayjson
import eway.json1 as einv
#from warnings import
#eway bill
from selenium import webdriver
from eway.automateeway import automate as automateeway
from eway.automateinv import automate as automateinv
from eway.automateinv import download as einvdownload

from eway.processeway import process
from win32com.client import Dispatch
from pythoncom import CoInitialize
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
#import dummybills.dummybills as dummybillsfeway
from dateutil.rrule import rrule, MONTHLY
import time
import threading
from credit.automatecredit import main as credit
#outstnading
from outstanding.main import outstanding
import shutil
import creditresolve 
#####
#####
#####
#####
from credit.removelock import main as removelock

def macroseway(filename) :
 CoInitialize()
 xl = Dispatch('Excel.Application')
 f=open('login.txt')
 excelpath=eval(f.read())['macro']
 f.close()
 wb = xl.Workbooks.Open('D:\\EWAY\\'+excelpath)
 writeData = wb.Worksheets('Main')
 writeData.Cells(13,5).Value = filename+'.xlsx'
 xl.visible =True
app = Flask(__name__)
@app.route('/removelock')
def removelocks():
    removelock()

@app.route('/comp/<month1>/<year1>')
def x(month1,year1) :
    halfpath='C:\\Users\\'+desktopuser+'\Desktop\GST\\'+month1+'-'+year1+'\\'
    pathcsv=halfpath+month1+'-'+year1+'.csv'
    gstmain.comp(pathcsv,halfpath)
    return render_template_string("<button onclick='window.open('/stop','_blank')'>Finish</button>")
@app.route('/creditresolve/<status>')
def creditres(status) :
    if status!="stop" :
     creditresolve.main() 
     return render_template_string("<button onclick='window.open('/stop','_blank')'>Finish</button>")
    else :
     creditresolve.close() 
     return render_template_string("<p>Finished succesfully</p>")
@app.route('/shogun') 
def shoguns() :
  Shogun.automate()
  return "Finished updating" 
@app.route('/extrabill/generatemonth/<month>') 
def generatemonth(month) :
    folders1 = os.listdir('D:\\extrabill\\'+month)
    folders ={}
    for i in folders1 :
        folders[i.split('.')[0]]=month+'..'+i
    return render_template('extrageneratefile.html',files=folders)

@app.route('/extrabill/generateall') 
def generateall() :
    folders1 = os.listdir('D:\\extrabill')
    folders = []
    for i in folders1 :
      if '-' in i :
          folders.append(i)
    return render_template('extrageneratemonth.html',folders=folders)
@app.route('/extrabill/report/<month>') 
def extrabillsreport(month) :
    if month=='all' :
      folders = os.listdir('D:\\extrabill')
      return render_template('extrabillsreport.html',folders=folders)
    else :
       df,df1,partywise=[],[],[]
       files=os.listdir('D:\\extrabill\\'+month)
       for i in files :
        x=pd.read_excel('D:\\extrabill\\'+month+'\\'+i,skiprows=5)
        df.append(x)
        wb = openpyxl.load_workbook('D:\\extrabill\\'+month+'\\'+i)
        sheet = wb.active
        partywise.append([i.split('-')[1],float(sheet['D1'].value)])
        #print(i)
        x['Party Name']=i.split('-')[1]
        df1.append(x)
       df=pd.concat(df,axis=0)
       print(df)
       df=pd.pivot_table(df,index=['PRODUCT'],values=['CASES'],aggfunc=np.sum)
       df1=pd.concat(df1,axis=0)
       df2=df1.copy()
       df1=pd.pivot_table(df1,index=['Party Name'],values=['MRP'],aggfunc=np.sum)
       partywise=pd.DataFrame(partywise,columns=['PARTY NAME','VALUE'])
       partywise=pd.pivot_table(partywise,index=['PARTY NAME'],values=['VALUE'],aggfunc=np.sum)
       with pd.ExcelWriter('D:\\extrabill\\report\\report - '+month+'.xlsx') as writer:
        df.to_excel(writer, sheet_name='Product')
        partywise.to_excel(writer, sheet_name='Party')
        df2.to_excel(writer, sheet_name='Master')
       return send_file('D:\\extrabill\\report\\report - '+month+'.xlsx',as_attachment=True)

@app.route('/extradownload/<filename>',methods=['POST','GET'])
def extradownload(filename) :
    return send_file('D:\\extrabill\\'+filename.replace('..','\\'),as_attachment=True)
@app.route('/extrabill/generate/<filename>')
def generatebill(filename) :

    df = pd.read_excel('D:\\extrabill\\'+filename.replace('..','\\'),skiprows=5)
    wb = openpyxl.load_workbook('D:\\extrabill\\'+filename.replace('..','\\'))
    sheet = wb.active
    dummybills.generatebills(sheet['B4'].value,sheet['B3'].value,sheet['B2'].value,df)
         
@app.route('/extrabill/stop',methods=['POST']) 
def extrastop() :
  global status
  status='stop'
  return 'stop'
@app.route('/extrabill/start',methods=['POST']) 
def extrastart() :
  global status
  path='D:\\extrabill\\data\\'
  options = webdriver.ChromeOptions()
  prefs = {'download.default_directory' : path }
  options.add_experimental_option('prefs', prefs)
  driver=webdriver.Chrome(r'chromedriver.exe',options=options)
  dummybills.getbill(driver)
  global dprice
  dprice = pd.DataFrame()
  def pricefunc() :
      intial=os.listdir(path)
      f=open('extrabill/price.txt')
      x=f.read()
      f.close()
      x=x.replace('_date1_',datetime.now().strftime('%d/%m/%Y'))
      x=x.replace('_date2_',datetime.now().strftime('%Y/%m/%d'))
      intial=os.listdir(path)
      driver.execute_script(x)
      while True :
       if len(os.listdir(path))== len(intial)+1 :
        try :
         file1=list((set(os.listdir(path))^set(intial))&set(os.listdir(path)))[0]
         if 'tmp' not in file1 and 'crd' not in file1:
           df = pd.read_excel(path+file1)
           df=df[[df.columns[1],df.columns[5]]]
           global dprice
           dprice=df
           print(2)
           break
         else :
             time.sleep(0.5)
        except Exception as e:
         print(e)
         continue
       else :
         time.sleep(0.5) 
  
          
  pricethread = threading.Thread(target=pricefunc)
  pricethread.start()
  driver.execute_script('var salesman,beat;')
  while True :
     try :
      #driver.switch_to.default_content()
      #print(driver.execute_script('return document.querySelector("#rsu-popup-billingTag > div.rsu-popup-action-bar > div > div > div > a.rsu-btn.rsu-btn-small.rsu-popup-action-btn.rsu-popup-action-ok.horizontal").innerText'))
      driver.execute_script('document.querySelector("#rsu-popup-billingTag > div.rsu-popup-action-bar > div > div > div > a.rsu-btn.rsu-btn-small.rsu-popup-action-btn.rsu-popup-action-ok.horizontal").addEventListener("click",function () {beat = document.querySelector("#bill_beat").value; salesman = document.querySelector("#bill_salesman").value;});')
      break
     except Exception as e:
         time.sleep(1)
         print(e)
  status='start'
  while True :
    if status=='stop' :
     pricethread.join()
     print(dprice)
     def mrp(pcode) :
         dprice1=dprice[dprice[dprice.columns[0]] == pcode]
         dprice1=dprice1.reset_index(drop=True)
         #dprice.to_excel('d.xlsx')
         #print(dprice1.iloc[0])
         return dprice1.iloc[0][dprice.columns[1]]
     
     y=driver.execute_script('return document.querySelector("#rsu-popup-billing_main_window-grid-area").innerHTML;')
     y1=pd.read_html(y)
     prod=y1[0]
     prod = prod[[prod.columns[1],prod.columns[2],prod.columns[5]]]
     prod = prod[prod[prod.columns[0]].notna()]
     prod['Mrp'] = prod[prod.columns[0]].apply(lambda x : mrp(x))
     prod.columns = pd.Series(['CODE','PRODUCT','CASES','MRP'])
     party=driver.execute_script('return document.querySelector("#billPartyName").value;')
     total =driver.execute_script('return document.querySelector("#bill_net_amt_bot").value ;')
     salesman=driver.execute_script('return salesman')
     beat=driver.execute_script('return beat')
     details=pd.DataFrame([['Date',datetime.now().strftime('%d/%m/%Y'),'Orignal price', total], ['Party Name',party,'Discount',''] , ['Beat',beat,'Net Amount',''],['Salesman',salesman,'',''] ])
     moc=datetime.now().strftime('%m-%y')
     paths = 'D:\\extrabill\\'+moc +'\\'
     if os.path.exists(paths) :
      filename=str(len(os.listdir(paths))+1)+'-'+party+'.xlsx'
     else :
      os.makedirs(paths)
      filename=str(len(os.listdir(paths))+1)+'*'+party+'.xlsx'
     driver.save_screenshot(paths+filename.split('.')[0]+'.png') 
     with pd.ExcelWriter(paths+filename) as writer:
      details.to_excel(writer,index=False,header=False)
      prod.to_excel(writer,startrow=5,index=False)
     print(salesman,beat,total)
     return json.dumps({'file':moc+'..'+filename});#moc+'..'+filename
     break 
    else :
     print(status)
     time.sleep(1)
@app.route('/extrabill')
def extrabill() :
 return render_template('extrabill.html')
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
@app.route('/eway/save',methods=['POST','GET'])
def saveeway() :
         x=request.form
         data={}
         for key in x.keys() :
           if key!='vehicle'  :
             data[key]=x[key]
         f=open('eway\\log.txt','w')
         f.write(str(data))
         f.close()
         return redirect('/eway')
@app.route('/eway/download/<date1>',methods=['POST','GET'])
def ewayc(date1) :
    if date1=='today' :
     date1=datetime.now().strftime('%d/%m/%Y')
    x={'date':date1}
    date=x['date'].split('-')[2]+'/'+x['date'].split('-')[1]+'/'+x['date'].split('-')[0]
    automateeway(0,date,'download')
    return "<script> window.open('','_self').close()</script>"

@app.route('/eway/generate',methods=['POST','GET'])
def generateeway() :
         start=time.time()
         x=request.form
         data={}
         for key in x.keys() :
           if key!='vehicle' and key!='date1' and key!='date2':
             data[key]=x[key]
         types = data['type']
         del data['type']
         f=open('eway\\log.txt','w')
         f.write(str({}))
         f.close()
         date1=x['date1'].split('-')[2]+'/'+x['date1'].split('-')[1]+'/'+x['date1'].split('-')[0]
         if x['date2']!='' :
          date2=x['date2'].split('-')[2]+'/'+x['date2'].split('-')[1]+'/'+x['date2'].split('-')[0]
         else :
             date2=date1
         def einvoicegenerate() :
          df=automateinv(data,date1,date2)
          if len(df.index)==0 :
             return "<script>alert('No record found')</script>"
          filename=datetime.now().strftime('%d-%m-%y')
          filename.replace('-','.')
          totaleinv = einv.create(df,filename)
          filename+='.json'
          if totaleinv != 0 :
           einvfile,ds = einvsite(filename)
           einvdownload(einvfile,df)
          print('Finished in : ',time.time()-start,'seconds')
         def ewaygenerate() :
            df=automateeway(data,date1,date2)
            if len(df.index)==0 :
             return "<script>alert('No record found')</script>"
            filename=datetime.now().strftime('%d-%m-%y')
            filename.replace('-','.')
            ewayjson.create(df,filename)
            filename+='.json'
            accept,error=ewaysite(filename)
            print('Finished in : ',time.time()-start,'seconds')
         if types == 'Both' :
            einvoicegenerate()
            ewaygenerate()
         elif types == 'EINVOICE' :
             einvoicegenerate()
         else :
             ewaygenerate()
         return "<p>Success</p>"

@app.route('/download/<filename>',methods=['POST','GET'])
def download(filename) :
    return send_file(filename.replace('..','\\'),as_attachment=True)


@app.route('/eway')
def indexeway():
   global useraccess   
   if useraccess['outstanding']==False :
       return render_template('pricing.html',err='outstanding',useraccess=useraccess)
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

######
######
######



#gst index
def create(month1,year1,mode='automatic',filename='1') :
    global halfpath
    global outerpath
    global path
    global pathcsv
    halfpath='C:\\Users\\'+desktopuser+'\Desktop\GST\\'+month1+'-'+year1+'\\'
    outerpath='C:\\Users\\'+desktopuser+'\Desktop\GST\\'
    if mode=='automatic' :
     pathx=outerpath+list(automategst(month1+'-'+year1,outerpath))[0]
    else :
        pathx=outerpath+filename
    os.makedirs(halfpath)
    df=pd.read_csv(pathx,dtype={'HSN':str,'Outlet Code':str })
    pathcsv=halfpath+month1+'-'+year1+'.csv'
    path=halfpath+'Error Report.xlsx'
    start = time.time()
    df=clean(df)
    print('clean csv ',time.time() - start)
    start = time.time()
    df.to_csv(pathcsv)
    print('writing csv ',time.time() - start)
    return errsuccess(1,month1,year1)
@app.route('/gst/errsuccess',methods=['GET','POST'])
def errsuccess(x=0,month2='',year2='') :
    global path
    global pathcsv
    global halfpath
    global outerpath
    try :
     os.remove(path)
    except:
      gg=0
    if x==1 :
        return render_template("changegst.html")  
    err,df,inv,rep,short=gstmain.main(pathcsv,path,halfpath,outerpath)
    s=[]
    if err==0 :
         for idx,row in inv.iterrows() :
             s.append([row['name'],row['value'],row['change'],row['details'],str(idx)])
         return render_template("GSTerror.html",s=s)
    else :
        return render_template("GSTsuccess.html",short=short)
@app.route('/gst/firsttimeerrsuccess',methods=['GET','POST'])
def firsttimeerrsuccess() :
    global path
    global pathcsv
    global halfpath
    global outerpath
    try :
     os.remove(path)
    except:
      gg=0
    start = time.time()
    err,df,inv,rep,short=gstmain.main(pathcsv,path,halfpath,outerpath)
    print('comp main',time.time()-start)
    s=[]
    if err==0 :
         for idx,row in inv.iterrows() :
             s.append([row['name'],row['value'],row['change'],row['details'],str(idx)])
         return render_template("GSTerror.html",s=s)
    else :
        return render_template("GSTsuccess.html",short=short)
    
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
def  downloadcurrent() :
    global halfpath
    try :
     return send_file(halfpath+'gst.json',as_attachment=True)
    except :
        return "<p> Go to Desktop >> GST >> MONTH-YEAR>> gst.json</p>"
@app.route('/gst/dels/<month1>/<year1>', methods = ['GET', 'POST'])
def dels(month1,year1) :
    global desktopuser
    f=open('C:\\Users\\'+desktopuser+'\Desktop\GST\\log.txt')
    prevs=eval(f.read())
    f.close()
    afters=[]
    for i in prevs :
        if i!='C:\\Users\\'+desktopuser+'\Desktop\GST\\'+month1+'-'+year1+'\\' :
            afters.append(i)
    f=open('C:\\Users\\'+desktopuser+'\Desktop\GST\\log.txt','w+')
    f.write(str(afters))
    f.close()
    shutil.rmtree('C:\\Users\\'+desktopuser+'\Desktop\GST\\'+month1+'-'+year1+'\\')
    return redirect('/gst')
@app.route('/gst/view/<month>/<year>',methods = ['GET', 'POST'])
def view(month,year) :
    global useraccess 
    if useraccess['gst']==False :
       return render_template('pricing.html',err='gst',useraccess=useraccess)
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
        return render_template('GSTview.html',month=month,year=year,short=short,alreadyerr=alreadyerr)
    else:
        return render_template('GSTview.html',month=month,year=year,short=short,pathjson=halfpath+'gst.json')
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
@app.route('/gst/report',methods=['POST','GET'])
def gstreport() :
    if request.method!='POST' :
     return render_template('gstreport.html')
    else :
        err=[]
        reportdup=[]
        data=request.form 
        strt_dt = date(int(data['year1']),int(data['month1']),1)
        end_dt = date(int(data['year2']),int(data['month2']),1)
        dates = [dt for dt in rrule(MONTHLY, dtstart=strt_dt, until=end_dt)]
        for i in dates :
           year,month=str(int(i.year)),str(int(i.month))
           if os.path.exists('C:\\Users\\'+desktopuser+'\Desktop\GST\\'+month+'-'+year+'\\short.txt') :
               f=open('C:\\Users\\'+desktopuser+'\Desktop\GST\\'+month+'-'+year+'\\short.txt')
               reportdup.append(eval(f.read()))
               f.close()
           else :
               err.append(month+'-'+year)
        values={}
        for j in reportdup : 
         for i in j :
          if i[0] not in values.keys():
             values[i[0]]=i[1:]
          else:
             values[i[0]]=[int(i[k])+int(values[i[0]][k-1]) for k in range(1,4)]
        dfreport=pd.DataFrame.from_dict(values)
        dfreport=dfreport.T
        dfreport.columns=['Invoice Value','Taxable','Total tax']
        dfreport['Central Tax']=dfreport['Total tax']/2
        if len(err)==0 :
         dfreport.to_excel('C:\\Users\\'+desktopuser+'\Desktop\GST\\report.xlsx',sheet_name='Report')
         return send_file('C:\\Users\\'+desktopuser+'\Desktop\GST\\report.xlsx',as_attachment=True)
        else :
            with pd.ExcelWriter('C:\\Users\\'+desktopuser+'\Desktop\GST\\report.xlsx') as writer:
             dfreport.to_excel(writer,sheet_name='Report')
             pd.DataFrame.from_dict({'error' :err}).to_excel(writer,sheet_name='Error')
            return send_file('C:\\Users\\'+desktopuser+'\Desktop\GST\\report.xlsx',as_attachment=True)
        
           

@app.route('/gst',methods=['POST','GET'])
def gst():
   global useraccess
   global desktopuser
   if useraccess['gst']==False :
       return render_template('pricing.html',err='gst',useraccess=useraccess)
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
       names[i]=month_name[int(i.split('-')[0])]+ ' , ' + i.split('-')[1]
   return render_template('GSTindex.html',months=months1,shorts=shorts,names=names)
#####
#####
######
#####
#####
@app.route('/usersave',methods=['POST'])
def usersave() :
    data=request.form
    datagst,datalogin={},{}
    gstkeys=['desktopuser','version','gstnumber']
    for i in data.keys() :
        if i in gstkeys :
            datagst[i]=data[i]
        else :
            datalogin[i]=data[i]
    f=open('GST\\gst.txt','w')
    f.write(str(datagst))
    f.close()
    f=open('login.txt','w')
    f.write(str(datalogin))
    f.close()
    return redirect('/home')


@app.route('/user') 
def userchange() :
     f=open('login.txt')
     logindata=eval(f.read())
     f.close()
     f=open('GST\\gst.txt')
     gstdata=eval(f.read())
     f.close()
     return render_template('user.html',userdata=logindata,gstdata=gstdata)
@app.route('/gst/manual',methods=['POST']) 
def manual() :
   global desktopuser
   if request.method == 'POST':
    month1=request.form['month']
    month1=str(int(month1))
    year1=request.form['year']
    if os.path.exists('C:\\Users\\'+desktopuser+'\Desktop\GST\\'+month1+'-'+year1+'\\') :
     return redirect('/gst/view/'+month1+'/'+year1)
    else :
     files=request.files['file']  
     files.save(os.path.join('C:\\Users\\'+desktopuser+'\Desktop\GST\\', files.filename))
     return create(month1,year1,'manual',files.filename)

@app.route('/home')
def home() :
    global userdata
    """"f=open('login.txt')
    f1=eval(f.read())
    sync=f1['sync']
    if sync!=datetime.now().strftime('%d-%m-%Y') :
     t1 = threading.Thread(target=credit)
 
     t2 = threading.Thread(target=getoutstanding,args=('today',))
     t3 = threading.Thread(target=ewayc,args=('today',))
     t1.start()
     t2.start()
     t3.start()
     f=open('login.txt','w+')
     f1['sync']=datetime.now().strftime('%d-%m-%Y')
     f.write(str(f1))
     f.close()"""
    #t3 = threading.Thread(target=automateeway)
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
    global useraccess
    useraccess=doc.to_dict()
    f=open('GST\\gst.txt')
    desktopuser=eval(f.read())['desktopuser']
    f.close()
    webbrowser.open('http://localhost:1000/home')
    app.run(host='localhost',port='1000',threaded=True)
else:
    sys.exit()



