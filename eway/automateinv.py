from selenium import webdriver
from datetime import datetime
import time
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from eway.processinv import process
import os
from os import listdir
from threading import Thread
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
def tab(name) :
  global driver
  while True : 
   try :
    driver.execute_script("document.getElementById('ikea_home_menu_search').value='';")
    break
   except :
       time.sleep(0.5)
       continue
  element=driver.find_element(By.ID,'ikea_home_menu_search')
  element.send_keys(name)
  time.sleep(2)
  waituntil('document.querySelector("#search_menu_item_container > div:nth-child(1)").click();')

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
def automate(data,date1,date2) :
    path='D:\\dataEWAY\\'
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    prefs = {'download.default_directory' : path }
    options.add_experimental_option('prefs', prefs)
    global driver
    driver = webdriver.Chrome(r'chromedriver.exe',options=options)
    return automates(data,date1,date2,driver)
    
def reader1(x,y) :
    global df
    df=pd.read_excel(x+y)
def reader2(x,y) :
    global df_2
    df_2=pd.read_excel(x+y,usecols=['Unnamed: 1','Bill Wise Sales'])

def download(filename,df) :
 def getajax(name) :
     return ajax.split('_'+name+'_')[1]
 with open('ajax.txt') as f :
     ajax = f.read()
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
      print(1)
      break 
   except Exception as e1:
        print(e1)
        if t2>=10 :
            break
        for t1 in range(0,1) :
          try :
            driver.execute_script('document.querySelector("#ikea_home_menu_search").click();')
          except : 
           time.sleep(1)
        if t1 == 0 :
            continue 
        break
 time.sleep(0.5)
 tab('E-Invoice IR')
 driver.switch_to.window(driver.window_handles[1])
 driver.find_element(By.ID,"attach_file").send_keys(filename)
 driver.execute_script("uploadMethod();")
 driver.close()
 driver.switch_to.window(driver.window_handles[0])
 bills = list(set(list(df['Document Number'])))
 intial = listdir(path)
 pdffiles = []
 for bill in bills :
   _pdf = getajax('billpdf').replace('_billfrom_',bill).replace('_billto_',bill) 
   pdf = driver.execute_script(_pdf).split('/')[-1]
   for sleep in range(0,200) : 
     files = list( (set(listdir(path))^set(intial))& set(listdir(path)) )
     if pdf in files :
         pdffiles.append(pdf)
         break 
     else :
         time.sleep(0.5)
 print(pdffiles)
def automates(data,date1,date2,driver) : 
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
      print(1)
      break 
   except Exception as e1:
        print(e1)
        if t2>=10 :
            break
        for t1 in range(0,1) :
          try :
            driver.execute_script('document.querySelector("#ikea_home_menu_search").click();')
          except : 
           time.sleep(1)
        if t1 == 0 :
            continue 
        break
 time.sleep(0.5)
 print(data)
 #split bills and beats
 f=open('eway\\vehicle.txt')
 vehname=eval(f.read())
 f.close()
 bills,beats=[],[]
 for s in data.keys() :
     if '.' in s :
         beats.append(s[1:])
     else :
         bills.append(s)
 final=[]
 dateeway1=date1.split('/')[2]+date1.split('/')[1]+date1.split('/')[0]
 dateeway2=date2.split('/')[2]+date2.split('/')[1]+date2.split('/')[0]
 print(bills,beats)
 if len(bills)>0 :
  intial=os.listdir(path)
  f=open(r'eway\inv.txt')
  x=f.read()
  f.close()
  x=x.replace('__beat__','')
  x=x.replace('__from__',dateeway1)
  x=x.replace('__to__',dateeway2)
  print(x)
  driver.execute_script(x)
  print(1)
  while True :
   if len(os.listdir(path))== len(intial)+1 :
     try :
         file1=list((set(os.listdir(path))^set(intial))&set(os.listdir(path)))[0]
         if 'tmp' not in file1 and 'crd' not in file1:
           df = pd.read_excel(path+file1)
           print(df)
           break
         else :
             time.sleep(0.5)
     except Exception as e:
        print(e)
        continue
   else :
      time.sleep(0.5) 
  time.sleep(0.2)
  print(bills)
  df=df[df['Document Number'].isin(bills)]
  l=process(df,data)
  print(l)
  final.append(l)
 if len(beats) > 0 :
  intial=os.listdir(path)
  f=open(r'eway\beat.txt')
  x=f.read()
  f.close()
  x=x.replace('__from__',dateeway1)
  x=x.replace('__to__',dateeway2)
  x=waituntil(x)
  vehicle={}
  print(x,1,2)
  for i in list(set(list(data.values()))) :
     vehicle[i]=[]
  print(x,beats)
  for i in x :
   for j in beats :
     if ''.join(j.split(' ')) in ''.join(i[1].split(' ')) :
        vehicle[data['.'+j]]+=[str(i[0])]
  if len(list(vehicle.keys()))==0 :
      return 'No such beats found : '+'\n'.join([s[1] for s in x])
  f=open(r'eway\inv.txt')
  x=f.read()
  f.close()
  x=x.replace('__from__',dateeway1)
  x=x.replace('__to__',dateeway2)
  for each in vehicle.keys() :
   intial=os.listdir(path)
   print(vehicle,vehicle[each])
   x1=x.replace('__beat__',','.join(vehicle[each]))
   print(x1)
   driver.execute_script(x1)
   while True :
    if len(os.listdir(path))== len(intial)+1 :
     try :
         file1=list((set(os.listdir(path))^set(intial))&set(os.listdir(path)))[0]
         if 'tmp' not in file1 and 'crd' not in file1:
           print(each,file1)
           dfv = pd.read_excel(path+file1)
           dfv['Vehicle No']=each
           dfv['Trans Name']=vehname[each]
           dfv['Distance level(Km)']=3
           dfv=dfv[dfv['Buyer GSTIN'].notna()]
           final.append(dfv)
           print('Finsihed',each,file1)
           break
         else :
             time.sleep(0.5)
     except Exception as e:
        print(e)
        continue
    else :
      time.sleep(0.5)  
 time.sleep(0.2)
 driver.quit()
 if len(final)==0 :
     return 0
 return pd.concat(final,axis=0)
path='D:\\dataEWAY\\'

