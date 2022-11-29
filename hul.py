import imp
import logging
from urllib import response
from Sessions import Session
from datetime import datetime
import json
from collections import defaultdict
import curlify
import pandas as pd
from flask import jsonify, send_file, make_response
import ewaysite
import einvsite
from io import BytesIO
import json_converter
import outstanding
import openpyxl
from itertools import combinations



REPORT_URL = "/rsunify/app/reportsController/generatereport.do"
AJAX_FILE = r"ajax.txt"


# small functions
def date(): return int((datetime.now() - datetime(1970, 1, 1)
         ).total_seconds() * 1000) - (330*60*1000)


class ikea(Session):
    def __init__(self, user, db, isReload = True ):
        super().__init__()
        self.db = db
        self.user = user
        with open(AJAX_FILE) as f:
          self.ajax_template = eval(f.read())
        if isReload : 
            self.reload()
        self.json = {'Content-type': "application/json; charset=utf-8"}
        self.download = lambda url: self.get(
            "/rsunify/app/reportsController/downloadReport?filePath="+url)
     
    def post(self, url, **kwargs):
        url = self.baseUrl + url if self.baseUrl not in url else url 
        kwargs["url"] = url
        res = super().post(**kwargs)
        # print(curlify.to_curl(res.request))
        #print(res.text)
        if res.status_code == 200:
            return res
        else:
            self.login()
            print("retry")
            self.post(**kwargs)

    def ajax(self, key, replaces):
        temp = {}
        for key, value in self.ajax_template[key].items():
            if type(value) == str:
               for orig, repl in replaces.items():
                   value = value.replace("_"+orig+"_", repl)
               temp[key] = value
        return temp

    def get(self, url, **kwargs):
        url = self.baseUrl + url
        res = super().get(url, **kwargs)
        if res.status_code == 200:
            return res
        else:
            self.login()
            self.get()

    def reload(self):
        self.cookies.clear()
        session = self.db.find_one({"username": self.user})
        if session and "session" in session.keys():
           cookies = json.loads(session["session"])
           for key, value in cookies.items():
               self.cookies.set(key, value)
           for attr in ["baseUrl", "ikea_user", "ikea_pwd", "dbName"]:
             self.__setattr__(attr, session[attr])
        else:
            self.login()

    def login(self):
        self.cookies.clear()
        data = self.db.find_one({"username": self.user})
        for attr in ["baseUrl", "ikea_user", "ikea_pwd", "dbName"]:
            self.__setattr__(attr, data[attr])

        data = {'userId': self.ikea_user, 'password': self.ikea_pwd,
            'dbName': self.dbName, 'datetime': date(), 'diff': -330}
        res = self.post('/rsunify/app/user/authentication.do',
                  data=data).text   # need to handle errors
        if "<body>" in res : 
             return False , "Login Credentials is Wrong ."
        if "Invalid" in res : 
            return False , res 
        if res == "CLOUD_LOGIN_PASSWORD_EXPIRED" : 
           self.post("/rsunify/app/masterPasswordController/lemonPasswordReset", data = {
            "newpassword": self.ikea_pwd , "confirmpassword": self.ikea_pwd }) 
           return self.login() 


        res = self.post("/rsunify/app/user/authenSuccess.htm")
        if res.status_code != 200 :
            return False 
        # store the session cookies in db
        self.db.update_one({"username": self.user}, {
                           "$set": {"session": json.dumps(dict(self.cookies))}})
        return True , "Successfully Login"

    def getBeats(self, fromDate, toDate):
        data = {'jasonParam': '{}',
            'procedure': 'Beat_Selection_Procedure', 'orderBy': '[MKM_NAME]'}
        data['jsonObjWhereClause'] = '{":P1": "' + fromDate.strftime(
            "%Y%m%d") + '",":P2": "' + toDate.strftime("%Y%m%d") + '",":P3":"Both",":P4":"SecBills"}'
        res = self.post(
            "/rsunify/app/reportsController/getReportScreenDatawithprocedure.do", data=data)
        # beats is returned in text format [[1,'AKBAR'],[4,'THIRU']]
        beats = json.loads(res.text)

        clean = lambda x:   max(x.replace(" ", "-").replace("+", "-").split("-"),key=len)
        beats = list(map(lambda x: [ x[0], clean(x[1]) ], beats))
        #additional cleaning : 
        isSame = lambda s1 , s2 :   (len( list(set(s1) ^ set(s2)) ) <= 1 ) or  s1 in s2 or s2 in s1 
        
        temp = defaultdict(list)
        for beatId, beatName in beats:
            for alreadyBeat in temp.keys() :  
               if isSame(alreadyBeat,beatName) : 
                 temp[alreadyBeat].append(beatId)
                 break 
            else : 
                temp[beatName].append(beatId)

        beats = dict((key, tuple(val)) for key, val in temp.items())
        return beats

    def Edownload(self, type, fromDate, toDate, data, beats, vehicles):
        fromDate, toDate = fromDate.strftime(
            "%Y%m%d"), toDate.strftime("%Y%m%d")
        billwise_data = {}
        excel_data = []
        for key, value in data.items():  # key is beat or billno , value is vehicle name
            if "-" in key:  # bills
                [fromBill, toBill] = key.split("-")
                data = self.ajax(type + "_download", {"fromDate": fromDate, "toDate": toDate,
                          "beats": "", "fromBill": fromBill, "toBill": toBill})
            else:  # beats
                data = self.ajax(type + "_download", {"fromDate": fromDate, "toDate": toDate,
                          "beats": ",".join([str(i) for i in beats[key]]), "fromBill": "", "toBill": ""})
            res = self.post(REPORT_URL, data=data)

            if res.text.strip() == "":
                continue  # nothing to download
            binary_content = self.download(res.text).content

            excel = pd.read_excel(BytesIO(binary_content))
            # if type == "eway" :  #eway bill transporter details
            excel["Trans Name"] = value["vehicle"]
            excel["Vehicle No"], excel["Distance level(Km)"] = value["vehicle"], value["distance"]
            excel_data.append(excel)

        if len(excel_data) == 0:
              return False
        return pd.concat(excel_data)  # the final dataframe

    def EGenerate(self, types, fromDate, toDate, data, beats, vehicles):
         maps = {"eway":  {"esession": ewaysite.Eway, "json":  json_converter.ewayJson},
           "einvoice":  {"esession": einvsite.Einvoice, "json": lambda data: json_converter.einvJson(data, isVeh=True)}}

         esession = maps[types]["esession"]()
         if not esession.reload(self.user, self.db):  # reloading failed
             return jsonify({"err": "Relogin Again"}), 520

         data = self.Edownload(types, fromDate, toDate, data, beats, vehicles)
         if type(data) == bool and data == False:
            return jsonify({"err": "No Data Found"}), 521

         json_data = maps[types]["json"](data)
         return jsonify(esession.upload(json_data))

    def outstanding(self, date=None , days = 20):
        salesman = self.post("/rsunify/app/paginationController/getPopScreenData", data= json.dumps({
            "jasonParam": { "viewName":"VIEW_LOAD_SALESMAN_BEAT_LINK_SALESMAN_LIST"}
        }) , headers = self.json ).json() 
        sal_id = map( lambda x : x[1] , salesman[0][1:])
        beats_data = []
        day = date.strftime('%A').lower() + "Linked"

        for id in sal_id : 
             beats_data += self.post("/rsunify/app/salesmanBeatLink/getSalesmanBeatLinkMappings",
                      data={"divisionId": 0, "salesmanId": int(id) }).json()
        beats_data = pd.DataFrame(beats_data)
        #print(beats_data.columns)
        beats_data.to_excel("exc.xlsx")
        filteredBeats = list(set(beats_data[beats_data[day] != '0']["beatId"]))
        
       
        data =  self.ajax("outstanding_download", {"date" : date.strftime("%Y-%m-%d") , "beats": ",".join(filteredBeats)})
    

        res = self.post("/rsunify/app/reportsController/generatereport.do" , data = data )
        binary_content = self.download(res.text).content
        excel = pd.read_excel(BytesIO(binary_content))
    
        return send_file(outstanding.interpret(excel,days) , as_attachment=True , download_name="outstanding.xlsx")

    def creditlock(self , config ) :
        config = config.find_one({"username" : self.user})["creditlock"] 
        default = config["OTHERS"]
        del config["OTHERS"]
        config = dict(sorted(config.items(), key=lambda item:  item[1] if item[1] != 0 else 10000 , reverse=True))
        
        partyMaster = pd.read_excel("/home/venkatesh/Downloads/party.xlsx" , skiprows = 9)
        partyMaster["PAR CODE HLL"] = partyMaster["HUL Code"]


        url =self.post("/rsunify/app/reportsController/generatereport.do" , data = self.ajax("creditlock_download",{})).text 
        creditlock_binary = BytesIO(self.download(url).content)
        
        creditlock = pd.read_excel(creditlock_binary)
        
        def beatType(beat) : 
            for type , max_bills in config.items() : 
                if type in beat : 
                   return max_bills
            return default 
            
        partyMaster["max_bills"] = partyMaster["Beat"].apply(beatType)
        partyMaster =  partyMaster.drop_duplicates(subset=['PAR CODE HLL'], keep='first')[["PAR CODE HLL","max_bills"]]

        creditlock = pd.merge(creditlock , partyMaster , on = "PAR CODE HLL",how="left")
        
        max_finder = lambda row : max(row["PAR CR BILLS UTILISED"],row["max_bills"]) if row["max_bills"] != 0 else 0
        creditlock["max_bills"] = creditlock.apply( max_finder , axis = 1 )
        creditlock = creditlock[creditlock["max_bills"] != creditlock['PAR CR BILLS']]
        creditlock_binary.seek(0)
        
        
        wb = openpyxl.load_workbook(creditlock_binary)
        ws = wb['Credit Locking']
        col = 6 
        for idx , row in creditlock.iterrows() : 
            ws.cell( int(row["Sr No"]) + 1 , 6).value = row["max_bills"]
        
        x = BytesIO()
        wb.save(x)
        x.seek(0)

        files = { "file" : ("credit.xlsx", x ,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  }
        res = self.post("/rsunify/app/beatSequenceMaster/uploadFileCLSU", files = files ).text 
        return  jsonify({ "count" : len(creditlock.index)  , "res" : res }) , 200   

