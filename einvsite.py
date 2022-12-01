from datetime import date, datetime, timedelta
import hashlib
import logging
from random import random
from time import time
from urllib import request
from Sessions import Session
import pandas as pd
import json
from io import BytesIO, StringIO
from bs4 import BeautifulSoup
EWAY_REPORT_DEFAULT_DAYS = 5




def myHash(str) : 
  hash_object = hashlib.md5(str.encode())
  md5_hash = hash_object.hexdigest()
  return hashlib.sha256(md5_hash.encode()).hexdigest()

def extractForm(html) :
  soup = BeautifulSoup(html, 'html.parser')
  form = {  i["name"]  : i.get("value","") for i in soup.find("form").find_all('input', {'name': True}) }
  return form 
           
headers = { "Referer": "https://einvoice1.gst.gov.in/" , 
            "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36" }

class Einvoice(Session) : 
      def __init__(self) :
        logging.debug("Einvoice Session class intiated") 
        self.captcha = ""
        super().__init__()
       
    
      def reload(self,user,db) : 
        self.db = db 
        self.cookies.clear()
        session = self.db.find_one({"username" : user})
        if session and "einv_session" in session.keys() and session["einv_session"] != None :
           cookies = json.loads(session["einv_session"])
           logging.debug("E-invoice db cookies fetched , cookies :: " , cookies )
           for key ,value in cookies.items() : 
               self.cookies.set(key,value,domain="einvoice1.gst.gov.in")
           res = self.get("https://einvoice1.gst.gov.in/Home/MainMenu",headers=headers) #check if logined correctly .
           if "https://einvoice1.gst.gov.in/Home/MainMenu" not in res.url : #reload faileD
              logging.debug(f"E-invoice reload with db cookies failed , response url : {res.url} , text : {res.text}")
              self.db.update_one( {"username" : user } ,{"$set" :{ "einv_session" : None }} )
              return True

           for attr in ["einv_user","einv_password"] :
               self.__setattr__(attr,session[attr])
           logging.debug(f"Einvoice reload successfull from db old cookie session")
           return True 
        logging.debug("No cookies available in db for einvoice")
        return False 

      def getCaptcha(self) : 
         home = self.get("https://einvoice1.gst.gov.in" , headers=headers).text 
         form = extractForm(home)
         captchaImg = self.get("https://einvoice1.gst.gov.in/get-captcha-image" , headers = headers).content 
         with open("captcha.aspx","wb+") as f : 
             f.write(captchaImg)
         return BytesIO(captchaImg) , {"cookies" : dict(self.cookies) , "form" : form } 

      def login(self,user,db,data) :
          form , captcha , cookies = data["form"] , data["captcha"] , data["cookies"]
          user_data = db.find_one({"username" : user})
          self.user , self.pwd  =  user_data["einv_user"] , user_data["einv_password"] 
          self.captcha = captcha 

          for key ,value in cookies.items() : 
               self.cookies.set(key,value,domain = "einvoice1.gst.gov.in")

          hsh1 = myHash(self.pwd) #password hashing 
          hsh2 = hashlib.sha256((hsh1 + form["UserLogin.Salt"]).encode()).hexdigest()
          form["UserLogin.Password"]  , form["CaptchaCode"] = hsh2 , self.captcha 
          form["UserLogin.UserName"] = self.user   
          res = self.post("https://einvoice1.gst.gov.in/Home/Login" , headers = headers , data = form )
          
          if res.url == "https://einvoice1.gst.gov.in/Home/Login" : #reload failed
               if "alert('Invalid Login Credentials" in res.text :  #credentials wrong 
                   return {"status" : False , "err" : "Wrong Credentials"}
               if "alert('Invalid Captcha" in res.text :  #captca wrong 
                   return {"status" : False , "err" : "Wrong Captcha"}
               return {"status" : False , "err" : "Unkown error"}
          
          db.update_one( {"username" : user } ,{"$set" :{ "einv_session" : json.dumps(dict(self.cookies)) }} )  
          return {"status" : True }
          
      def upload(self,json_data) : 
          
          bulk_home = self.get("https://einvoice1.gst.gov.in/Invoice/BulkUpload" , headers=headers).text
          
          files = { "JsonFile" : ("eway.json", StringIO(json_data) ,'application/json') }
          form = extractForm(bulk_home)
           
          upload_home = self.post("https://einvoice1.gst.gov.in/Invoice/BulkUpload" ,  files = files , headers=headers , data = form ).text
          success_excel = pd.read_excel(BytesIO(self.get("https://einvoice1.gst.gov.in/Invoice/ExcelUploadedInvoiceDetails" , headers=headers).content))
          failed_excel =  pd.read_excel(BytesIO(self.get("https://einvoice1.gst.gov.in/Invoice/FailedInvoiceDetails" , headers=headers).content))
          data = { "download" :  success_excel.to_csv(index = False) ,  
                     "success" : len(success_excel.index) , "failed" : len(failed_excel.index) , "failed_data" : failed_excel.to_csv(index=False) } 
          return  data
          
      def report(self,fromDate = datetime.now() -timedelta(days=EWAY_REPORT_DEFAULT_DAYS) ,toDate = datetime.now())  : 
        tempFrom = fromDate  
        data =[]
        while tempFrom <= toDate : 
          report_home = self.get("https://ewaybillgst.gov.in/Reports/CommomReport.aspx?id=3",headers = headers).text 
          form = extractForm(report_home) 
          form["ctl00$ContentPlaceHolder1$txtDate"] = tempFrom.strftime("%d/%m/%Y")  
          tempFrom += timedelta(days=EWAY_REPORT_DEFAULT_DAYS)  
          form["ctl00$ContentPlaceHolder1$txtDate1"] = min(tempFrom , toDate).strftime("%d/%m/%Y") 
          report = self.post("https://ewaybillgst.gov.in/Reports/CommomReport.aspx?id=3",headers = headers , data = form ).text 

          soup = BeautifulSoup(report, 'html.parser')
          table = str(soup.find(id="ctl00_ContentPlaceHolder1_tr_data").select_one("td div table"))
          excel = pd.read_html(StringIO(table))[0]
          data.append(excel)
        report = pd.concat(data).dropna(subset=["EWB.No"]).reset_index() 
        return report 





# eway = Eway() 
# form,cookie = eway.getCaptcha() 

# eway = Eway() 
# eway.setCaptcha(input("captcha : ") , cookie)
# eway.login(form,"DEVAKI9999","Mosl2121@") 
# eway.report( datetime(2022,9,1) , datetime(2022,9,20) )




             





# __LASTFOCUS: 
# __EVENTTARGET: 
# __EVENTARGUMENT: 
# __VIEWSTATE: EMW06QL+oqvE8PGySuWJjyC2kYEpdmYIS4SretTrbPeMRdmrCxjA8cHUl9J3tNrI9a++A9glimQvT2TxacNvqNHuK4l2I4IPA6HYRwopCHY=
# __VIEWSTATEGENERATOR: C2EE9ABB
# __SCROLLPOSITIONX: 0
# __SCROLLPOSITIONY: 0
# __VIEWSTATEENCRYPTED: 
# __EVENTVALIDATION: YZm6p9Ap1YOM41HTzJ9Tv6FRW2e8gMgTayb2PCTzORL4FdbiEODZcxcyAk14hpMBH9cBye+pFBfJUPHrWFWchlPyDslC4pzHdvjpgLOX8+zyLa9S+ont33bdG8WEji/Nft8GWzQciOCBQRyJi9aTDTdjN5VaHU7Xl17aPWTuOZL2KqH/MzYouFVPvG/n94wczfBaeBhCprzykKaDo8+GAqoh7PD0rvbaCrMSO0zk/njFeIlhdH/zUxJ/2UEnqgeL
# HiddenField3: KVOu6xPeSOO1yla
# txt_username: DEVAKI9999
# txt_password: 83872db86b839e6e5dd3370232611518d7cb9564bacb49c9057a9cdfef297f9f
# txtCaptcha: V4N54
# btnLogin: Login
# hidSalt: 


# hash_md5 
# text = "Think and wonder, wonder and think."
# hash_object = hashlib.md5(text.encode())
# md5_hash = hash_object.hexdigest()
#  hashlib.sha256(md5_hash.encode())
#   var hsh = hex_md5(pwd);
#     var key = document.getElementById("HiddenField3").value;
#     var hsh1 = sha256_digest(hsh);
#     var hsh2 = sha256_digest(hsh1 + key);   
#     document.getElementById("txt_password").setAttribute("value", hsh2);
#     document.getElementById("txt_password").value = hsh2;
#     d = {e['name']: e.get('value', '') for e in html_proc.find_all('input', {'name': True})}




