from selenium import webdriver
from datetime import datetime
import time
from selenium.webdriver.common.keys import Keys
import os
def get(driver,x) :
 searchbox = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[1]/div[3]/div/div/input')
 driver.execute_script('document.querySelector("#gstin-search-form > div > div > input").value ="'+x+'"');
 searchbox1 = driver.find_element_by_xpath('/html/body/main/section[2]/div/div/div/div/form/div/div/button')
 searchbox1.click()
 g=0
 while 0 <1 :
     try :
          searchboxx = driver.find_element_by_xpath('/html/body/main/section[3]/div/div/div')
          searchboxx1 = driver.find_element_by_xpath('/html/body/main/section[3]/div/div/div/table/tbody/tr/td[10]')
          searchboxx2 = driver.find_element_by_xpath('/html/body/main/section[3]/div/div/div/table/tbody/tr/td[11]')
          if searchboxx1.get_attribute('innerHTML')=='Active' :
              stat=1 
          else :    
             stat=2
             g=searchboxx2.get_attribute('innerHTML')
          break
     except :
         try :
          searchboxx = driver.find_element_by_xpath('/html/body/main/div[1]/p')
          stat=0
          break
         except :
             time.sleep(1)
 #print(x,stat)
 return stat,g
def result(y,df):
 start  = time.time()
 options = webdriver.ChromeOptions()
 #options.add_argument("no-sandbox")
 #options.add_argument("--disable-gpu")
 options.add_argument("--window-size=1920,1080")
 options.add_argument("--start-maximized")
 #options.add_argument("--headless")
 #options.add_argument("--disable-dev-shm-usage")
 #options.set_headless()
 driver = webdriver.Chrome('chromedriver.exe',options=options)
 driver.maximize_window()
 driver.get('https://www.mastersindia.co/gst-number-search-and-gstin-verification/')
 acc=[]
 rej=[]
 cancel,canceldate=[],[]
 for i in y :
     ##print(i)
     t,g=get(driver,i)
     if t== 1:
         acc.append(i)
     elif t==0 :
         rej.append(i)
         driver.save_screenshot(str(i)+".png")
         
     else :
         p=df[df['GSTIN of Recipient']==i]
         if g=='' :
             print('server down in gst number check')
         driver.save_screenshot(str(i)+".png")
         if max(p['Invoice Date'].apply(lambda x: datetime.strptime(x,'%d/%m/%Y'))) >= datetime.strptime(g,'%d/%m/%Y') :
          cancel.append(i)
          canceldate.append(g)
 driver.quit()
 print('number' , time.time() -start )
 return acc,rej,cancel,canceldate

    

