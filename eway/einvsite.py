from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import win32com.client
import pandas as pd
import time 
from datetime import datetime
def einvsite(filename) :
 path='D:\\dataEWAY\\'
 options = webdriver.ChromeOptions()
 prefs = {'download.default_directory' : path }
 options.add_experimental_option('prefs', prefs)
# options.add_argument("--user-data-dir=D:/vs/devaki enterprises/Profile 1")
 driver = webdriver.Chrome(r'chromedriver.exe',options=options)
 driver.get('https://einvoice1.gst.gov.in/')
 driver.execute_script('document.querySelector("#btnLogin").click();')
 driver.execute_script('document.querySelector("#txtUserName").value="DEVAKI9999"')
 driver.execute_script('document.querySelector("#txt_password").value="Mosl2121@"')
 while True :
   try :
     if driver.execute_script('return document.querySelector("#txtUserName")') is None :
         break
     time.sleep(1)
   except :
     break

 driver.execute_script('window.location.href="https://einvoice1.gst.gov.in/Invoice/BulkUpload"')
 while True :
    try :
     driver.find_element(By.CSS_SELECTOR ,'input[type="file"]').send_keys("D:\\EINV\\"+filename)
     break
    except Exception as e:
        time.sleep(1)
        print(e)
 while True :
    try :
     driver.find_element(By.CSS_SELECTOR ,'input[type="submit"]').click()
     break
    except Exception as e:
        time.sleep(1)
        print(e)
 time.sleep(2)
 driver.execute_script('window.location.href="https://einvoice1.gst.gov.in/MisRpt"')
 driver.execute_script('document.querySelector("#FromDate").value="'+datetime.now().strftime('%d/%m/%Y')+'"')
 driver.execute_script('document.querySelector("#ToDate").value="'+datetime.now().strftime('%d/%m/%Y')+'"')
 driver.execute_script('document.querySelector("#btngo").click()')
 time.sleep(3)
 intial = os.listdir(path)
 driver.execute_script('window.location.href="https://einvoice1.gst.gov.in/MisRpt/ExcelGenerratedIrnDetails"')
 while True :
  try :
   if len(os.listdir(path))==len(intial)+1 : 
    filename = list((set(os.listdir(path))^set(intial))&set(os.listdir(path)))[0]
    if ('tmp' not in filename) and 'crd' not in filename : 
     df = pd.read_excel(path+filename)
     break
  except Exception as e:
     time.sleep(0.5)
     print(e)
 print(path+filename)
 return path+filename,df
#waysite('26-12-21.json')