import pandas as pd
import numpy as np
from selenium import webdriver
from datetime import datetime
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
def waituntil(x) :
  global driver
  for i in range(60) :
    try :
      driver.execute_script(x)
      break
    except :
      continue
def tab(name) :
  global driver
  element=driver.find_element(By.ID,'ikea_home_menu_search')
  element.send_keys(name)
  time.sleep(2)
  driver.execute_script('document.querySelector("#search_menu_item_container > div:nth-child(1)").click();')
def dialogbox(trigger,value) :
  driver.find_element(By.ID,trigger).send_keys(Keys.RETURN)
  time.sleep(2)
  driver.find_element(By.ID,'inputSrId').send_keys(value)
  time.sleep(0.5)
  driver.find_element(By.ID,"rsu-popup-salesman_list > div.rsu-popup-footer > div > div.rsu-popup-col.rsu-popup-col-3.rsu-popup-embeded-right-col > div > a.rsu-btn.rsu-btn-small.rsu-popup-action-btn.rsu-popup-action-ok.horizontal").click()
  print(1)
  time.sleep(0.5)
def main() :
 global driver
 f=open(r'login.txt')
 login=eval(f.read())
 f.close()
 website=login['website']
 user,password,rs=login['user'],login['password'],login['rs']
 options = webdriver.ChromeOptions()
 options.add_argument("--window-size=1920,1080")
 options.add_argument("--start-maximized")
 driver = webdriver.Chrome(r'chromedriver.exe',options=options)
 if int(login['headless'])==1 :
  driver.set_window_position(-10000,0)
 date=datetime.now()
 driver.maximize_window()
 driver.get(website)
 searchbox = driver.find_element_by_xpath('//*[@id="userName"]')
 searchbox.send_keys(user)
 searchbox1 = driver.find_element_by_xpath('//*[@id="password"]')
 searchbox1.send_keys(password)
 searchbox = driver.find_element_by_xpath('//*[@id="databaseName"]')
 searchbox.send_keys(rs)
 but = driver.find_element_by_xpath('//*[@id="gologin"]')
 but.click()
 #checking for captcha and fro login loading main page 
 while True:
  try :
    driver.execute_script("document.getElementById('ikea_home_menu_search').click()")
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
      waituntil("document.getElementById('ikea_home_menu_search').click()")
      break
 time.sleep(1)
 tab('BILLING')
 time.sleep(5)
 dialogbox('bill_salesman','CHARLES N')
 time.sleep(10)
 print(1)
 dialogbox('bill_beat','d-')
 time.sleep(0.5)
 driver.execute_script('document.querySelector("#rsu-popup-billingTag > div.rsu-popup-action-bar > div > div > div > a.rsu-btn.rsu-btn-small.rsu-popup-action-btn.rsu-popup-action-ok.horizontal").click();')
 time.sleep(1)
 for i in range(3) :
  try:
   driver.execute_script('document.querySelector("#Ok").click();')
  except : 
   break
main()

 
