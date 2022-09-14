# Generated by Selenium IDE
import time
import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import openpyxl
from IMP.main import  *
import pandas as pd

def main() :
   driver = login(path)
   beats = ajax_plain(driver,'/rsunify/app/reportsController/getReportScreenData?jasonParam={"viewName":"OUTLET_OLD_BEAT_FILTERS_CREDITLIMIT"}')
   beats = {beat[2] : beat[1] for beat in beats[0][1:] } #transform the data into { beatname : beatkeyinteger(string) }
   def retail_condition(beat_name) : 
       if 'FG' in beat_name.split('-') or 'WHOLESALE' in beat_name  or 'OTR' in beat_name:
           return False 
       return True
   def fg_condition(beat_name) : 
       if 'FG' not in beat_name.split('-') or 'WHOLESALE' in beat_name or 'OTR' in beat_name :
           return False 
       return True
   retail = { key : value for key,value in beats.items() if retail_condition(key) }
   fg = { key : value for key,value in beats.items() if  fg_condition(key) }
   
   beatkeys = ','.join(retail.values())
   replaces = {'beatkeys':beatkeys}
   retail = report_ajax(driver,'creditlockdown',replaces,make_download=True)

   beatkeys = ','.join(fg.values())
   replaces = {'beatkeys':beatkeys}

   fg = report_ajax(driver,'creditlockdown',replaces,make_download=True)
   def change(fpath,minimum) :
    df = pd.read_excel(fpath)
    df['New Limit'] = df['PAR CR BILLS UTILISED'].apply(lambda limit :  max(limit,minimum) )
    df.to_excel(fpath.split('.')[0]+'s.xlsx')
    wb = openpyxl.load_workbook(fpath)
    ws = wb['Credit Locking']
    startcol = 6
    startrow = 2
    for limit in df['New Limit'] :
     ws.cell(startrow, startcol).value = limit
     startrow +=1
    wb.save(fpath)
   def upload(fpath):
    driver.find_element(By.ID,"attach_file").send_keys(fpath)
    driver.execute_script("uploadMethod();")
    while True :
      if 'Uploaded' in driver.execute_script('return document.querySelector("#display-message").innerText') :
          print('Finished',fpath)
          break
      else :
          time.sleep(0.5)
   WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.ID,"ikea_home_menu_search"))).send_keys("CREDIT LOCK") #open credit lock for uploading 
   waituntil(driver,'document.querySelector("#search_menu_item_container > div:nth-child(1)").click();')
   driver.switch_to.window(driver.window_handles[1])
   change(retail,1)
   upload(retail)
   change(fg,2)
   upload(fg)
   driver.close()
   driver.quit()

path='D:\\devaki-data\\creditlock\\'    

  
  
