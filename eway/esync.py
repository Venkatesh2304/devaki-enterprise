from collections import defaultdict
from typing import DefaultDict
from selenium import webdriver
from datetime import datetime
import time
from selenium.webdriver.common.action_chains import ActionChains
from eway.einvsite import *
from eway.EGenerate import *
import pandas as pd
from datetime import timedelta 
from IMP.main import *
from collections import defaultdict
path = "D:\\devaki-data\\eway\\"
def sync() : 
    driver = einvlogin()
    einv_df = einvreport(driver,False)["data"]
    einv_df["Doc Date"]= einv_df["Doc Date"].apply(lambda date_str : datetime.strptime(date_str,"%d-%m-%Y"))
    einv_df  = einv_df[einv_df["Doc Date"] >= datetime.now() - timedelta(days = 2) ] 
    driver_ikea = login(path)
    df = download_e("einvoice", (datetime.now() - timedelta(days = 2)).strftime("%d/%m/%Y") ,datetime.now().strftime("%d/%m/%Y")
                        ,driver=driver_ikea,data ={".ALL":"TN45AP3219"})
    intersection = set ( einv_df["Doc No"] ) ^ set( df["Document Number"] )
    missing = list(intersection & set(df["Document Number"]))
    cancel = list(intersection & set(einv_df["Doc No"]))
    missing = missing[:3]
    if len(missing) == 0 : 
        return {"Total Bills" : 0 , "Total Uploaded" : 0 , "Total Failed":0 , "Canceled" : cancel } 
    filename =   path + "einvoice.json" 
    missing = df[df["Document Number"].apply(lambda inv : inv in missing)]
    json_einvoice.create(missing,filename,ewb_data=False)
    
    cancel = df[df["Document Number"].apply(lambda inv : inv in cancel)]
    json_einvoice.create(cancel,filename,ewb_data=False)
    json_einvoice.create(missing,filename,ewb_data = False) 

    upload_response = einvupload(driver,filename)
    upload_response["Canceled"] = "\n".join(list(set(cancel["Document Number"])))

    response = einvreport(driver)
    df = response["data"]
    df = df[df["Doc No"].apply(lambda inv :  inv in missing )]
    driver_ikea.execute_script("displayScreen_reports('reportsController','reportScreen','E-Invoice IRN Upload', 'Utility/eInvoiceIRNUpload')")
    driver_ikea.switch_to.window(driver_ikea.window_handles[1])
    for i in range(30) :
      try :
         driver_ikea.find_element_by_id("attach_file").send_keys(response["fpath"])
         break 
      except :
          time.sleep(1)
    driver_ikea.execute_script("uploadMethod();")
    driver_ikea.close()
    return upload_response 






