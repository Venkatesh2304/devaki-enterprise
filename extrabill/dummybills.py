import pandas as pd
import numpy as np
from selenium import webdriver
from datetime import datetime
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
def getbill(driver1) :
 global driver
 driver=driver1
 f=open(r'login.txt')
 login=eval(f.read())
 f.close()
 website=login['website']
 user,password,rs=login['user'],login['password'],login['rs']
 #if int(login['headless'])==1 :
 # driver.set_window_position(-10000,0)
 user='CREDIT'
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
 
 
def generatebills(salesman,beat,party,prods) :
    global driver
    #user,password,rs='SA','Mosl1234@@','41A392'
    user,password,rs='CREDIT','Ven2004@','41A392'
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    prefs = {'profile.managed_default_content_settings.images':2,'disk-cache-size':4096}
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(r'chromedriver.exe',options=options)
    driver.maximize_window()
    driver.get('https://leveredge102.hulcd.com/rsunify/')
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
      driver.find_element(By.ID,"ikea_home_menu_search").send_keys("BILLING")
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
      WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.ID,"ikea_home_menu_search"))).send_keys("BILLING")
      break
    waituntil('document.querySelector("#search_menu_item_container > div:nth-child(1)").click();')
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "bill_salesman"))) 
    actions = ActionChains(driver)
    actions.double_click(element).perform()
    while True :
     try :
      WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "inputSrId"))).send_keys(salesman)
      break
     except :
         actions.double_click(element).perform()
         time.sleep(2)
         
    time.sleep(2)
    driver.find_element(By.ID, "inputSrId").send_keys(Keys.ENTER)
    time.sleep(1)
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "bill_beat")))
    actions = ActionChains(driver)
    actions.double_click(element).perform()
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "inputSrId"))).send_keys(beat)
    time.sleep(2)
    driver.find_element(By.ID, "inputSrId").send_keys(Keys.ENTER)
    time.sleep(1)
    driver.find_element(By.LINK_TEXT, "Ok").click()
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "Ok"))).click() 
    driver.execute_script('document.querySelector("body > div.rsu-probe-container.rsu-box-shadow.ui-draggable").style.left="100px";document.querySelector("body > div.rsu-probe-container.rsu-box-shadow.ui-draggable").style.top="420px"')   
   
    element = driver.find_element(By.ID, "billPartyName")
    actions = ActionChains(driver)
    actions.double_click(element).perform()
    WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID,"inputSrId"))).send_keys(party)
    time.sleep(1)
    while True :
     try :
      if party not in driver.execute_script('return document.querySelector("#rsu-popup-party_name-grid-area tr:nth-child(1) > td:nth-child(2)").innerText') : 
          time.sleep(1)
          continue
      WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#rsu-popup-party_name-grid-area tr:nth-child("+str(1)+") > td:nth-child(2)"))).click()
      break
     except Exception as e:
        print(e)
        time.sleep(1)
        try :
         driver.find_element(By.LINK_TEXT, "Ok").click()
        except :
            print(1)
        try :
         driver.find_element(By.ID, "Ok").click()
        except :
            print(1)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, ".rsu-embed-footer-action-bar > .rsu-popup-action-ok").click()
    WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID,"par_cpl_ok"))).click()
    i = 0
    for idx,row in prods.iterrows() :
       i+=1
       eachprod(row['CODE'],row['PRODUCT'],row['CASES'],i)
       print(1)
def eachprod(pkd,name,qty,ele) :
    element = driver.find_element(By.CSS_SELECTOR, "#rsu-popup-billing_main_window-grid-area > table > tbody > tr:nth-child("+str(ele)+") > td:nth-child(2)")
    actions = ActionChains(driver)
    actions.double_click(element).perform()
    time.sleep(1)
    for k in name : 
     WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID,"inputSrId"))).send_keys(k)
     n=0
     l=0
     while True :
        n+=1
        try : 
         print(pkd,driver.execute_script('return document.querySelector("#rsu-popup-product_list_mrp-grid-area > table > tbody > tr:nth-child('+str(n)+') > td:nth-child(3)").innerText'))
         if pkd ==  driver.execute_script('return document.querySelector("#rsu-popup-product_list_mrp-grid-area > table > tbody > tr:nth-child('+str(n)+') > td:nth-child(3)").innerText') :
               driver.execute_script('document.querySelector("#rsu-popup-product_list_mrp-grid-area > table > tbody > tr:nth-child('+str(n)+') > td:nth-child(3)").click()')
               time.sleep(0.5)
               l=1
               break
        except Exception as e:
            print(e)
            break
     if l==1 :
         break
    
    """while True :
     try :
      driver.find_element(By.ID, "inputSrId").send_keys(name)
      break
     except :
      time.sleep(1)
      ele-=1
      element = driver.find_element(By.CSS_SELECTOR, "#rsu-popup-billing_main_window-grid-area > table > tbody > tr:nth-child("+str(ele)+") > td:nth-child(2)")
      actions = ActionChains(driver)
      actions.double_click(element).perform()
      time.sleep(1)
    for j in range(30) :
     try :
      if name in WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="rsu-popup-product_list_mrp-grid-area"]/table/tbody/tr[1]/td[2]'))).get_attribute('innerText') :
        break
      else :
       time.sleep(0.5)
     except :
        driver.execute_script("document.getElementById('inputSrId').value='';")
        time.sleep(1)
        driver.find_element(By.ID, "inputSrId").send_keys(name)
        time.sleep(1)
        continue"""
    WebDriverWait(driver,15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".rsu-embed-footer-action-bar > .rsu-popup-action-ok"))).click()
    print(2)
    time.sleep(1)
    print('document.querySelector("#rsu-popup-billing_main_window-grid-area > table > tbody > tr:nth-child('+str(ele)+') > td:nth-child(6)").innerText =  "'+str(qty)+'";')
    driver.find_element(By.CSS_SELECTOR, '#rsu-popup-billing_main_window-grid-area > table > tbody > tr:nth-child('+str(ele)+') > td:nth-child(6)').click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, '#rsu-popup-billing_main_window-grid-area > table > tbody > tr:nth-child('+str(ele)+') > td:nth-child(6)').send_keys(int(qty))
    #waituntil('document.querySelector("#rsu-popup-billing_main_window-grid-area > table > tbody > tr:nth-child('+str(ele)+') > td:nth-child(6)").innerText =  "'+str(qty)+'";')
    print(3)
