import pandas as pd
from selenium import webdriver
driver=webdriver.Chrome(r'chromedriver.exe')
driver.get('https://leveredge102.hulcd.com/rsunify/app/user/authenSuccess.htm#!')
x=input()
y=driver.execute_script('return document.querySelector("#rsu-popup-billing_main_window-grid-area").innerHTML;')
print(y)

y1=pd.read_html(y)
print(y1)