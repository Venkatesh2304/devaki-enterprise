from IMP.main import login 
from IMP.main import openexcel 
from IMP.main import waituntil 
from selenium import webdriver 
from selenium.webdriver.common.by import By
from datetime import datetime 
import pandas as pd 
import openpyxl
import os 
import time
import win32com.client
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def main() :
   date=datetime.now().strftime('%Y-%m-%d')
   global path 
   path = 'D:\\'
   global driver
   driver = login(path)
   time.sleep(1)
   f=open('creditsales.txt')
   temp=f.read()
   f.close()
   temp = temp.split('_part_')
   curr =  temp[0]
   files=os.listdir(path)
   driver.execute_script(curr)
   df=pd.DataFrame()
   for i in range(60) :
        if len(os.listdir(path))-len(files)==1 :
            filename = list( (set(os.listdir(path))^set(files))&set(os.listdir(path)) )[0]
            if '.crd' in filename or '.tmp' in filename :
                continue
            l=0
            try :
             df = pd.read_excel(path+filename)
            except :
                l=1
                continue
            if(l==0) :
             break 
        else :
            time.sleep(1)
            continue 
   curr = temp[3] 
   curr=curr.replace('_importdate_',date)
   orders=driver.execute_script(curr) 
   orders = orders['quantumImportList']
   shops  = {}
   for i in orders :
       if i['parName'] not in shops.keys() and i['allocQty']!=0 and 'WHOLESALE' not in i['mkmName'] :
           shops[i['parName']]=i['salName'] 
   print(shops) 
   o = win32com.client.Dispatch("Excel.Application")
   o.Interactive = False
   o.Visible = False
   wb = o.Workbooks.Open(path+filename)
   fs = wb.ActiveSheet
   lastrow = fs.UsedRange.Rows.Count
   for i in range(lastrow, 2, -1):
    if fs.Cells(i,3).Value not in shops.keys() or fs.Cells(i,6).Value < fs.Cells(i,9).Value :
        fs.Rows(i).EntireRow.Delete()
   os.remove(path+"creditlock.xlsx")
   wb.SaveAs(path+"creditlock.xlsx")
   o.Visible = True
   o.Interactive = True
   WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.ID,"ikea_home_menu_search"))).send_keys("CREDIT LOCK")
   waituntil(driver,'document.querySelector("#search_menu_item_container > div:nth-child(1)").click();')
   driver.switch_to.window(driver.window_handles[1])
def close() :
   driver.find_element(By.ID,"attach_file").send_keys(path+"creditlock.xlsx")
   driver.execute_script("uploadMethod();")
   while True :
      if 'Uploaded' in driver.execute_script('return document.querySelector("#display-message").innerText') :
          print('Finished')
          break
      else :
          time.sleep(1) 
   time.sleep(3)
   driver.close() 
