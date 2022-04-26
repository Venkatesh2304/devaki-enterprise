import pandas as pd
from selenium import webdriver
from time import sleep
from os import listdir
import datetime

f=open('out.txt')
y = f.read()
f.close() 
f=open(r'login.txt')
login=eval(f.read())
f.close()
website=login['website']
user,password,rs=login['useroutstanding'],login['passwordoutstanding'],login['rs']
path='D:\\tax\\'
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")
prefs = {'download.default_directory' : path }
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(r'chromedriver.exe',options=options)
driver.get(website)
searchbox = driver.find_element_by_xpath('//*[@id="userName"]')
searchbox.send_keys('CREDIT')
searchbox1 = driver.find_element_by_xpath('//*[@id="password"]')
searchbox1.send_keys(password)
searchbox = driver.find_element_by_xpath('//*[@id="databaseName"]')
searchbox.send_keys(rs)
but = driver.find_element_by_xpath('//*[@id="gologin"]')
but.click()
x = input()
driver.set_window_position(-10000,0)

date = datetime.datetime.strptime('01/04/2020','%d/%m/%Y')
while date <= datetime.datetime.strptime('01/04/2021','%d/%m/%Y'):
  y1 = y.replace('_to_',date.strftime('%Y-%m-%d'))
  y1 = y1.replace('_to1_',date.strftime('%d/%m/%Y'))
  #print(y1)
  #intial=listdir(path)
  driver.execute_script(y1)
  #print(s)
  #driver.execute_script("window.open('/rsunify/app/reportsController/downloadReport?filePath="+s+"','_blank') ;")
  date+=datetime.timedelta(days=1)
  sleep(0.25)

