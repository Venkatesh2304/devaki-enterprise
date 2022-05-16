from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import win32com.client
import pandas as pd
import time 
path = "D:\\devaki-data\\eway\\"
def ewaysite(filename) :
 options = webdriver.ChromeOptions()
 prefs = {'download.default_directory' : path }
 options.add_experimental_option('prefs', prefs)
 driver = webdriver.Chrome(r'chromedriver.exe',options=options)
 try :
   driver.get('https://ewaybillgst.gov.in/login.aspx')
 except :
     x=5
 with open("config.txt") as f :
    config = eval(f.read())
 while True :
  try :
   driver.execute_script(f'document.querySelector("#txt_username").value="{config["eway_user"]}"')
   driver.execute_script(f'document.querySelector("#txt_password").value="{config["eway_pass"]}"')
   break
  except :
      continue 
 while True :
   try :
     if driver.execute_script('return document.querySelector("#txt_username")') is None :
         break
     time.sleep(1)
   except :
     break

 driver.execute_script('window.location.href="https://ewaybillgst.gov.in/BillGeneration/BulkUploadEwayBill.aspx"')
 while True :
    try :
     driver.find_element(By.CSS_SELECTOR ,'input[type="file"]').send_keys(filename)
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

 WebDriverWait(driver, 10).until(EC.alert_is_present())
 driver.switch_to.alert.accept()
 while True :
    try :
     driver.find_elements(By.CSS_SELECTOR ,'input[type="submit"]')[1].click()
     break
    except Exception as e:
        time.sleep(1)
        print(e)
 intial = os.listdir(path)
 while True :
    try :
     z=0
     for i in driver.find_elements(By.CSS_SELECTOR ,'input[type="submit"]') :
         print(i.get_attribute('innerText'),0,i.get_attribute('value'),1,i.get_attribute('innerHTML'))
         if 'xport' in i.get_attribute('value') :
             i.click()
             z=1
             break  
     if z==1 :
        break
    except Exception as e:
        time.sleep(1)
        print(e)
 while True :
  try :
   if len(os.listdir(path))==len(intial)+1 : 
    filename = list((set(os.listdir(path))^set(intial))&set(os.listdir(path)))[0]
    df=pd.read_html(path+filename)
    break
  except Exception as e:
     time.sleep(0.5)
     print(e)
 df=df[0]
 return { "fpath" : path+filename ,"data" :  df }