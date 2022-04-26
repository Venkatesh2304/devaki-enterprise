from selenium import webdriver
from datetime import datetime
import time
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
from threading import Thread
import sys
import winsound
import pandas as pd
import win32com.client
     
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
def login(paths) :
 global path 
 path = paths
 options = webdriver.ChromeOptions()
 options.add_experimental_option('excludeSwitches', ['enable-logging'])
 options.add_argument("--window-size=1920,1080")
 options.add_argument("--start-maximized")
 prefs = {'download.default_directory' : path ,'safebrowsing.enabled': 'false',"profile.default_content_setting_values.automatic_downloads":1}
 options.add_experimental_option('prefs', prefs)
 driver = webdriver.Chrome(r'chromedriver.exe',options=options)
 f=open('login.txt')
 userdata=eval(f.read())
 f.close()
 if int(userdata['headless'])==1 :
  driver.set_window_position(-10000,0)
 user,password,rs=userdata['usereway'],userdata['passwordeway'],userdata['rs']
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
 t2=0
 while True:
   t2+=1
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
          try : 
              driver.find_element_by_xpath('//*[@id="userName"]')
          except :
              continue 
 while True :
  try :
   driver.execute_script('document.querySelector("#ikea_home_menu_search").click();') 
   break
  except :
     print('wait')
     time.sleep(0.5)
 print('finsihed')
 driver.set_script_timeout("300")
 return driver
def openexcel(filename,t=30) :
 o = win32com.client.Dispatch("Excel.Application")
 o.Visible = 1
 for i in range(t) :
  try :
   wb = o.Workbooks.Open(filename)
   break
  except Exception as e:
   time.sleep(1)
   print(e)
 ws = wb.Worksheets[0]
 return wb
def waituntil(driver,x,y=60) :
 for i in range(y):
  try :
    driver.execute_script(x)
    break
  except:
    time.sleep(1)
    print(1,x)
 if i==y:
   try :
     driver.execute_script('document.querySelector("body > div.panel.window.ui-draggable.ui-resizable.ui-resizable-disabled.messager-window > div.dialog-button.messager-button > a").click();')    
     time.sleep(1)
     driver.execute_script(x)
   except :
    x=1/0
def download(driver,dpath) :
   intial = list(set(os.listdir(path)))
   down = downt.replace('_dpath_',dpath)
   driver.execute_script(down)
   while True :
      final = list(set(os.listdir(path)))
      if len(final)-len(intial) == 1 : 
          fname = list((set(final)^set(intial))&set(final))[0] 
          if dpath.split('/')[-1] == fname :
            return path+fname
      else :
          time.sleep(0.5)
def ajax_plain(driver,url) :
    ajax = ajax_template.split('_plain_')[1]
    ajax = ajax.replace('_url_',url)
    print('plain')
    return driver.execute_script(ajax)
def report_ajax(driver,keyword,replaces,make_download=False) : 
    ajax = ajax_template.split('_'+keyword+'_')[1]
    for old,new in replaces.items() :
        ajax = ajax.replace('_'+old+'_',new)
    ajax += ajax_template.split('_ajax_')[1]
    data = driver.execute_script(ajax)
    if make_download : 
       fpath = download(driver,data)
       return fpath
    return data 
def data_ajax(driver,keyword,replaces={},content="json") :
    ajax = ajax_template.split('_'+keyword+'_')[1]
    ajax = ajax_template.split('_datarequest_')[1].replace("_data_",ajax) 
    for old,new in replaces.items() :
        ajax = ajax.replace('_'+old+'_',new)
    if content == "form" :
       ajax = ajax.replace('_content_',"application/x-www-form-urlencoded; charset=UTF-8")
    if content == "json" :
       ajax = ajax.replace('_content_',"application/json;charset=UTF-8;")
    data = driver.execute_script(ajax)
    return data
path = ''
base_url = 'leveredge102.hulcd.com'
with open('ajax.txt') as f :
    ajax_template = f.read()
downt = ajax_template.split('_download_')[1].replace('base_url',base_url)
