from pandas.core.indexes import datetimes
from selenium import webdriver
from datetime import datetime
import time
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
import sys
import winsound
import pandas as pd
def waitlog(reason,timeout=30) :
  global driver
  for i in range(timeout) :
   x=driver.execute_script('return document.querySelector("#display-message").innerText')
   if reason.lower() in x.lower() :
       time.sleep(1)
   else :
       break
  if i==30 :
    try :
     driver.execute_script('document.querySelector("body > div.panel.window.ui-draggable.ui-resizable.ui-resizable-disabled.messager-window > div.dialog-button.messager-button > a").click();')    
     time.sleep(1)
     driver.execute_script('return document.querySelector("#display-message").innerText')
    except :
     x=2/0
     
def waituntil(x) :
 global driver
 for i in range(60):
  try :
    print(x)
    return driver.execute_script(x)
    break
  except:
    time.sleep(1)
    print(1)
 if i==60 :
   x=1/0
def automate(data,date,types) :
   path='D:\\dataEWAY\\'
   if types!='download' :
       f=open('cache.txt')
       store=eval(f.read())['eway']
       store=store[0]
       return parser(data,store[0],store[1])
   else :
    automates(data,date,driver)
    
def automates(data,date) :
 options = webdriver.ChromeOptions()
 options.add_argument("--window-size=1920,1080")
 options.add_argument("--start-maximized")
 prefs = {'download.default_directory' : path }
 options.add_experimental_option('prefs', prefs)
 global driver
 driver = webdriver.Chrome(r'chromedriver.exe',options=options)
 f=open('login.txt')
 userdata=eval(f.read())
 f.close()
 if int(userdata['headless'])==1 :
  driver.set_window_position(-10000,0)
 user,password,rs=userdata['usereway'],userdata['passwordeway'],userdata['rs']
 #website=userdata['website']
 website=''
 #driver.set_window_position(-10000,0)
 driver.get('https://leveredge102.hulcd.com/rsunify/')
 searchbox = driver.find_element_by_xpath('//*[@id="userName"]')
 searchbox.send_keys(user)
 searchbox1 = driver.find_element_by_xpath('//*[@id="password"]')
 searchbox1.send_keys(password)
 searchbox = driver.find_element_by_xpath('//*[@id="databaseName"]')
 searchbox.send_keys(rs)
 but = driver.find_element_by_xpath('//*[@id="gologin"]')
 but.click()
 intial=os.listdir(path)
 f=open(r'eway\beat.txt')
 x=f.read()
 f.close()
 while True:
  try :
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
      break 
  except :
         break
 time.sleep(1)
 x=waituntil(x)
 print(x)
 getbeats=[]
 beats=['BEEMA']
 for i in x :
  for j in beats :
     if j in x[1] :
         getbeats.append(x[0])
 getbeats=list(set(getbeats))
 f=open(r'eway\eway.txt')
 x=f.read()
 f.close()
 x=x.replace('__beat__',','.join(getbeats))
 driver.execute_script(x) 
 f=open(r'eway\ewaybybill.txt')
 x=f.read()
 f.close()    
 bills=[['DEV37816','DEV37817'],['DEV37818','DEV37819'],['DEV37818','DEV37819'],['DEV37818','DEV37819'],['DEV37818','DEV37819']]
 for i in bills :
     x1=x.replace('__from__',i[0])
     x1=x1.replace('__to__',i[1])
     driver.execute_script(x1) 
 time.sleep(0.1)
 n = len(bills)+1
 while True :
  files=(set(os.listdir(path)) ^ set(intial))&set(os.listdir(path))
  if len(files)==n :
      for i in list(files) :
        if 'tmp' in i or 'crd' in i :
           continue 
      break 
  else :
      time.sleep(0.2)
 print(files)

path='D:\\dataEWAY\\'
automates(0,0)
