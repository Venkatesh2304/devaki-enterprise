from selenium import webdriver
from datetime import datetime
import time
from datetime import datetime
from selenium.webdriver.common.keys import Keys
import os
import calendar
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import glob
def waituntil(x,driver) :
 for i in range(60):
  try :
    print(x)
    driver.execute_script(x)
    break
  except:
    time.sleep(1)
    print(1)
 if i==60 :
   x=1/0

def automate(month,path) :
 f=open(r'login.txt')
 login=eval(f.read())
 f.close()
 website=login['website']
 user,password,rs=login['user'],login['password'],login['rs']
 options = webdriver.ChromeOptions()
 options.add_argument("--window-size=1920,1080")
 options.add_argument("--start-maximized")
 prefs = {'download.default_directory' : path }
 options.add_experimental_option('prefs', prefs)
 global driver
 driver = webdriver.Chrome(r'chromedriver.exe',options=options)
 if int(login['headless'])==1 :
  driver.set_window_position(-10000,0)
 driver.get(website)
 searchbox = driver.find_element_by_xpath('//*[@id="userName"]')
 searchbox.send_keys(user)
 searchbox1 = driver.find_element_by_xpath('//*[@id="password"]')
 searchbox1.send_keys(password)
 searchbox = driver.find_element_by_xpath('//*[@id="databaseName"]')
 searchbox.send_keys(rs)
 but = driver.find_element_by_xpath('//*[@id="gologin"]')
 but.click()
 from_date = '01/'+month.replace('-','/').zfill(7)+'"'
 d,last=calendar.monthrange(int(month.split('-')[1]),int(month.split('-')[0]))
 last=str(last)+'/'+month.replace('-','/').zfill(7)
 if datetime.strptime(last,'%d/%m/%Y') > datetime.now() :
     date=datetime.now()
     late=str(date.day).zfill(2)+'/'+ str(date.month+1).zfill(2)+'/'+ str(date.year)
 
 y = " $.ajax({type: 'POST',url: '/rsunify/app/gstReturnsReport/gstReturnReportGenerate?pramFromdate=" +from_date + "&paramToDate="+last+"&gstrValue=1&paramId=2',contentType: 'text',cache: false,success : function(data) {console.log(data);window.open('/rsunify/app/reportsController/downloadReport?filePath='+data,'_blank');}}) ;"

 while True:
  try :
   driver.find_element(By.ID,"ikea_home_menu_search").send_keys("")
   #driver.execute_script(y)
   break
  except :
      captcha=driver.find_element(By.ID,'cap_question')
      captcha=captcha.get_attribute('innerText')
      captcha=captcha.replace('=','')
      captcha=captcha.split('+')
      try :
       captcha=[int(i.strip()) for i in captcha]
      except :
        time.sleep(0.5)
        continue
      value=sum(captcha)
      driver.execute_script('document.getElementById("cap_answer").value='+str(value))
      driver.execute_script('confirmSubmission();')
      WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.ID,"ikea_home_menu_search"))).send_keys("")
      #waituntil(y)
      break
 driver.execute_script(y)
 intial=os.listdir(path)
 x=0
 while 0 <1 :
  if len(os.listdir(path))== len(intial)+1 :
   while 0 <1 :
     if 'crd' in list((set(os.listdir(path))^set(intial))&set(os.listdir(path)))[0] or '.tmp' in list((set(os.listdir(path))^set(intial))&set(os.listdir(path)))[0]:
         time.sleep(1)
     else :
         break
   break
  elif x==60 :
      print('Timeout automate and the program will close in 10 sec .Try manual')
      time.sleep(10)
      sys.exit()
      break
  else :
      x=x+1
      time.sleep(1)
 driver.quit() 
 return (set(os.listdir(path))^set(intial))&set(os.listdir(path))


