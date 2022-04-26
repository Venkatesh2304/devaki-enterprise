from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import win32com.client
import pandas as pd
import time 
def ewaysite(filename) :
 path='D:\\dataEWAY\\'
 options = webdriver.ChromeOptions()
 prefs = {'download.default_directory' : path }
 options.add_experimental_option('prefs', prefs)
# options.add_argument("--user-data-dir=D:/vs/devaki enterprises/Profile 1")
 driver = webdriver.Chrome(r'chromedriver.exe',options=options)
 try :
   driver.get('https://ewaybillgst.gov.in/login.aspx')
 except :
     x=5
 while True :
  try :
   driver.execute_script('document.querySelector("#txt_username").value="DEVAKI9999"')
   driver.execute_script('document.querySelector("#txt_password").value="Mosl2121@"')
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
     driver.find_element(By.CSS_SELECTOR ,'input[type="file"]').send_keys("D:\\EWAY\\"+filename)
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
    print(df)
    break
  except Exception as e:
     time.sleep(0.5)
     print(e)
 df=df[0]
 #df['Errors']=df['Errors'].apply(lambda x: x.split(':')[1].strip() )
 """print(df['Errors'])
 df1=df[df['Errors'].notna()]
 df=df[df['Errors'].isna()]
 df=df[list(df.columns)[:10]]
 df.to_excel(path+filename.split('.')[0]+'.xlsx',index=False)"""
 o = win32com.client.Dispatch("Excel.Application")
 o.Visible = 1
 for i in range(20):
  try :
   wb = o.Workbooks.Open(path+filename)
   break
  except Exception as e:
   time.sleep(1)
   print(e)
 ws = wb.Worksheets[0]
 ws.Columns.AutoFit()
 #ws.PageSetup.FitToPagesTall = False
 #ws.PageSetup.FitToPagesWide = 1
 return df,pd.DataFrame()
#waysite('26-12-21.json')