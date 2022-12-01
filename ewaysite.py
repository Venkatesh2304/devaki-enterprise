from datetime import date, datetime, timedelta
import hashlib
from Sessions import Session
import pandas as pd
import json
from io import BytesIO, StringIO
from collections import defaultdict
from bs4 import BeautifulSoup
EWAY_REPORT_DEFAULT_DAYS = 5


def parseEwayExcel(data) : 
    err_map = { "No errors" : lambda x : x == "" , "Already Generated" :  lambda x : "already generated" in x }
    err_list = defaultdict(list)
    for bill in data.iterrows() : 
        err = bill[1]["Errors"]
        Type = None
        for err_typ , err_valid in err_map.items() : 
            if type(err) == str and err_valid(err) :
               Type = err_typ 
               break 
        if Type == None : 
           Type = "Unknown error"
        err_list[Type].append( [ bill[1]["Doc No"] , err  ])
    return err_list

def myHash(str) : 
  hash_object = hashlib.md5(str.encode())
  md5_hash = hash_object.hexdigest()
  return hashlib.sha256(md5_hash.encode()).hexdigest()

def extractForm(html) :
  soup = BeautifulSoup(html, 'html.parser')
  form = {  i["name"]  : i.get("value","") for i in soup.find("form").find_all('input', {'name': True}) }
  return form 
           
headers = { "Referer": "https://ewaybillgst.gov.in/login.aspx" , 
            "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36" }

class Eway(Session) : 
      def __init__(self) : 
        self.captcha = "" 
        super().__init__()
        self.cookies.set("ewb_ld_cookie",value = "292419338.20480.0000" , domain = "ewaybillgst.gov.in")   
      
      def website(self) : 
          for i in range(30) : 
            try :
              home = self.get("https://ewaybillgst.gov.in/login.aspx", headers = headers,timeout = 3).text
              print("Done")
              break
            except :
              print("Retry : ",i)
              continue
          return home 

      def reload(self,user,db) : 
        self.db = db 
        self.cookies.clear()
        session = self.db.find_one({"username" : user})
        if session and "eway_session" in session.keys() and session["eway_session"] != None :
           cookies = json.loads(session["eway_session"])
           for key ,value in cookies.items() : 
               self.cookies.set(key,value,domain="ewaybillgst.gov.in")

           res = self.get("https://ewaybillgst.gov.in/mainmenu.aspx",headers=headers) #check if logined correctly .
           
           if res.url == "https://ewaybillgst.gov.in/login.aspx" : #reload faileD
              self.db.update_one( {"username" : user } ,{"$set" :{ "eway_session" : None }} )
              return False

           for attr in ["eway_user","eway_password"] :
               self.__setattr__(attr,session[attr])
           return True 
        return False 

      def getCaptcha(self,OldCookie = None ) : 
         ewaybillTaxPayer = "p5k4foiqxa1kkaiyv4zawf0c"   
         self.cookies.set("ewaybillTaxPayer",value = ewaybillTaxPayer, domain = "ewaybillgst.gov.in")
         
         home = self.website()
         form = extractForm(home)
         captchaImg = self.get("https://ewaybillgst.gov.in/Captcha.aspx" , headers = headers).content 
         
         #with open("captcha.aspx","wb+") as f : 
         #     f.write(captchaImg)

         return BytesIO(captchaImg) , {"cookies" : dict(self.cookies) , "form" : form } 

      def login(self,user,db,data) :
          form , captcha , cookies = data["form"] , data["captcha"] , data["cookies"]
          user_data = db.find_one({"username" : user})
          self.user , self.pwd  =  user_data["eway_user"] , user_data["eway_password"] 
          self.captcha = captcha 

          for key ,value in cookies.items() : 
               self.cookies.set(key,value,domain = "ewaybillgst.gov.in")

          hsh1 = myHash(self.pwd) #password hashing 
          hsh2 = hashlib.sha256((hsh1 + form["HiddenField3"]).encode()).hexdigest()
          form["txt_password"]  , form["txtCaptcha"] = hsh2 , self.captcha 
          form["txt_username"] = self.user  
          res = self.post("https://ewaybillgst.gov.in/login.aspx" , headers = headers , data = form )
     
          if res.url == "https://ewaybillgst.gov.in/login.aspx" : #reload failed
               if "alert('Invalid Login Credentials" in res.text :  #credentials wrong 
                   return {"status" : False , "err" : "Wrong Credentials"}
               if "alert('Invalid Captcha" in res.text :  #captca wrong 
                   return {"status" : False , "err" : "Wrong Captcha"}
               with open('res','w+') as f : 
                    f.write(res.text)
               return {"status" : False , "err" : "Unkown error"}
          db.update_one( {"username" : user } ,{"$set" :{ "eway_session" : json.dumps(dict(self.cookies)) }} )   
          return {"status" : True }
          
      def upload(self,json_data) : 
          bulk_home = self.get("https://ewaybillgst.gov.in/BillGeneration/BulkUploadEwayBill.aspx" , headers=headers).text
          
          files = { "ctl00$ContentPlaceHolder1$FileUploadControl" : ("eway.json", StringIO(json_data) ,'application/json') }
          headers["Referer"] =  "https://ewaybillgst.gov.in/BillGeneration/BulkUploadEwayBill.aspx"
          form = extractForm(bulk_home)
          del form["ctl00$ContentPlaceHolder1$btnGenerate"]
          form["ctl00$lblContactNo"] = ""
          del form["ctl00$ContentPlaceHolder1$FileUploadControl"]
          
          upload_home = self.post("https://ewaybillgst.gov.in/BillGeneration/BulkUploadEwayBill.aspx" ,  files = files , headers=headers , data = form ).text
          form = extractForm(upload_home)
          with open("A.html" , "w+" ) as f : 
              f.write(upload_home)
          generate_home = self.post("https://ewaybillgst.gov.in/BillGeneration/BulkUploadEwayBill.aspx" , headers=headers , data = form ).text 
          soup = BeautifulSoup(generate_home, 'html.parser')
          table = str(soup.find(id="ctl00_ContentPlaceHolder1_BulkEwayBills"))
          try :
            excel = pd.read_html(StringIO(table))[0]
          except : 
             if "alert('Json Schema" in upload_home :  #json schema is wrong 
                 return {"status" : False , "err" : "Json Schema is Wrong"}
          err = parseEwayExcel(excel)
          data = { "download" : excel.to_csv(index=False) }
          return data 
          
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




