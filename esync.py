from collections import defaultdict
from typing import DefaultDict
from selenium import webdriver
from datetime import datetime
from datetime import timedelta
import time
from selenium.webdriver.common.action_chains import ActionChains
from eway.einvsite import *
from eway.process import *
import pandas as pd
from IMP.main import *
import eway.json_einvoice as json_einvoice
import eway.json_eway as json_eway
from eway.EGenerate import download_e
from collections import defaultdict

def sync() : 
    driver = einvlogin()
    einv_df = einvreport(driver,False)
    einv_df["date"] = einv_df["Doc Date"].apply(lambda date : datetime.strptime(date,"%d-%m-%Y"))
    einv_df  = einv_df[einv_df["date"] >   (datetime.now() - timedelta(days = 3))  ]
    df = download_e("einvoice", (datetime.now() - timedelta(days = 2)).strftime("%d/%m/%Y") ,datetime.now().strftime("%d/%m/%Y")
                        ,driver=False,data ={".ALL":"TN45AP3219"})
    intersection = set ( einv_df["Doc No"] ) ^ set( df["Document Number"] )
    missing = list(intersection & set(df["Document Number"]))
    filename = datetime.now().strftime("%d-%m-%Y")
    missing = df[df["Document Number"].apply(lambda inv : inv in missing)]
    json_einvoice.create(missing,filename,ewb_data=False)
    cancel = list(intersection & set(einv_df["Doc No"]))
    response = einvupload(driver,filename+'.json')
    print(response)
sync()
