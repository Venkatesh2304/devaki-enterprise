from collections import defaultdict
from typing import DefaultDict
from selenium import webdriver
from datetime import datetime
import time
from selenium.webdriver.common.action_chains import ActionChains
from eway.einvsite import einvsite
from eway.ewaysite import ewaysite
from eway.process import *
import pandas as pd
from IMP.main import *
import eway.json_einvoice as json_einvoice
import eway.json_eway as json_eway
from collections import defaultdict

def sync() : 
    driver = einvlogin()
    einv_df = einvreport(driver,path,False)
    einv_df  = einv_df[einv_df["Doc Date"] >= datetime.now() - timedelta(days = 2) ]
    intersection = set ( einv_df["Doc No"] ) ^ set( df["Document Number"] )
    df = download_e(types, (datetime.now() - timedelta(days = 2)).strftime("%d/%m/%Y") ,datetime.now().strftime("%d/%m/%Y")
                        ,driver=False,data ={".ALL":"TN45AP3219"})
    missing = list(intersection & set(df["Document Number"]))
    filenanme = "x.json"
    missing = df[df["Document Number"].apply(lambda inv : inv in missing)]
    json_einvoice.create(missing,filename,ewb_data=False)
    cancel = list(intersection & set(einv_df["Doc No"]))

    cancel = df[df["Document Number"].apply(lambda inv : inv in cancel)]
    json_einvoice.create(cancel,filename,ewb_data=False)
    


    filename = date2.split('/')[0] +'-'+ date2.split('/')[1] +'-'+date2.split('/')[2]
    json_einvoice.create(missing,filename,ewb_data = False) 


    upload(driver,filename)
sync()
