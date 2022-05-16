from collections import defaultdict
from typing import DefaultDict
from selenium import webdriver
from datetime import datetime
import time
from selenium.webdriver.common.action_chains import ActionChains
from eway.ewaysite import ewaysite
import eway.einvsite as einvsite
from eway.process import *
import pandas as pd
from IMP.main import *
import eway.json_einvoice as json_einvoice
import eway.json_eway as json_eway
from collections import defaultdict
def EGenerate(types,date1,date2,data) :
   if types == "Both" : 
      emain("einvoice",date1,date2,False,data)
      return emain("eway",date1,date2,False,data)
   elif  types == "EINVOICE" : 
         emain("einvoice",date1,date2,False,data)
   else :
        return emain("eway",date1,date2,False,data)
def parseinput(data) : 
 bills,beats=[],[]
 for s in data.keys() :
     if '.' in s :
         beats.append(s[1:])
     else :
         bills.append(s)
 return bills,beats
def emain(types,date1,date2,driver,data) : 
    df = download_e(types,date1,date2,driver,data)
    filename = path + date2.split('/')[0] +'-'+ date2.split('/')[1] +'-'+date2.split('/')[2] + ".json"
    if types == "einvoice" : 
        json_einvoice.create(df,filename)
        driver = einvsite.einvlogin()
        einvsite.einvupload(driver,filename)
        response = einvsite.einvreport(driver)
        return response
    else : 
        json_eway.create(df,filename)
        response = ewaysite(filename)
        return response 

def download_e(etype,date1,date2,driver,data={},beats = [] ,bills = []) : 
 if driver == False :  
     driver = login(path)
 if etype == "einvoice" : 
   type_data = {"Doc Column": "Document Number" , "fileinfo" : {"title":"E Invoice,E Invoice","reportfilename":"E_Invoice",
                "viewpage":"Utility/eWayBillGeneration","viewname":"E_Invoice_Generation_SP"} ,"process":process_einvoice}
 else : 
     type_data = {"Doc Column": "Doc.No" , "fileinfo" : {"title":"E Way Bill,E Way Bill","reportfilename":"E_Way_Bill",
                   "viewpage":"Utility/eWayBillGeneration","viewname":"E_Way_Bill_Generation_SP"},"process":process_eway }
 with open("config.txt") as f : 
    bill_prefix = eval(f.read())["bill_prefix"]
 if len(beats) ==0 and len(bills) == 0 :
    if len(data.keys()) != 0 : 
      data = {  (key if "." in key else bill_prefix + key) : value  for key,value in data.items() }
      bills,beats = parseinput(data)
 if "ALL" in beats : 
     beats = [""]
     bills = [] 
     _data = {}
     _data["."] = data[".ALL"]
     del data 
     data = _data 
 final=[]
 fromd =date1.split('/')[2]+date1.split('/')[1]+date1.split('/')[0]
 tod =date2.split('/')[2]+date2.split('/')[1]+date2.split('/')[0]
 
 if len(bills)>0 :
    fpath = report_ajax(driver,"ebeat",{"from":fromd ,"to": tod,"beat": "", "fileinfo": str(type_data["fileinfo"]) },True)
    df = pd.read_excel(fpath)
    df=df[df[ type_data["Doc Column"] ].isin(bills)]
    filtered = type_data["process"](df,data)
    final.append(filtered)
 if len(beats) > 0 :
  beat_list = custom_ajax(driver,"getbeats",replaces = {"from":fromd,"to":tod})
  vehicles = defaultdict(list)
  for beat in beats : 
     for beat_ikea in beat_list : 
         if beat.strip().lower().replace(' ','') in beat_ikea[1].strip().lower().replace(' ','')   : 
                 vehicles[ data['.'+beat] ].append( beat_ikea[0] )
  for vehicle,beat_ids in vehicles.items() : 
     fpath = report_ajax(driver,"ebeat",{"from":fromd ,"to": tod,"beat":','.join([ str(b_id) for b_id in beat_ids])  ,
                                         "fileinfo": str(type_data["fileinfo"]) },True)
     df = pd.read_excel(fpath) 
     filtered = type_data["process"](df,data,vehicle)
     final.append(filtered)
 if len(final)==0 :
     return 0

 return pd.concat(final,axis=0)
driver = False 
path='D:\\devaki-data\\eway\\'

