from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import win32com.client
import pandas as pd
import time 
from datetime import datetime
path='D:\\dataEWAY\\'
def einvlogin() :
 options = webdriver.ChromeOptions()
 prefs = {'download.default_directory' : path }
 options.add_experimental_option('prefs', prefs)
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
 return driver 
def einvupload(driver,filename) : 
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
 table = "<table>"+driver.execute_script("return document.querySelector('table').innerHTML")+"</table>"
 upload_res  = pd.read_html(table)[0] 
 return upload_res 

def einvreport(driver,is_today = True) : 
 driver.execute_script('window.location.href="https://einvoice1.gst.gov.in/MisRpt"')
 if is_today :
    driver.execute_script('document.querySelector("#FromDate").value="'+datetime.now().strftime('%d/%m/%Y')+'"')
    driver.execute_script('document.querySelector("#ToDate").value="'+datetime.now().strftime('%d/%m/%Y')+'"')
 driver.execute_script('document.querySelector("#btngo").click()')
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
 return df