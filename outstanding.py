import pandas as pd
import numpy as np
from warnings import filterwarnings
import datetime
from IMP.main import * 

path = "D:\\devaki-data\\outstanding\\" 
def interpret(file,beats,days):
 beats = [ beat.strip() for beat in beats ]
 df=pd.read_excel(file)
 df = df.dropna(subset = ["Salesman"])
 df['party']=df['Party Name'].apply(lambda x: x.split('-')[0])
 df['Salesman']=df['Salesman'].apply(lambda x: x.split('-')[0])
 df = df[df['Beat Name'].apply(lambda beat :beat.strip() in beats)]
 unfiltered =df.copy()
 filtered =df[df['In Days'] > days ]
 pivot_filtered = pd.pivot_table(filtered,index=['Salesman','Beat Name','party'],values=['O/S Amount','In Days'],aggfunc={'O/S Amount':np.sum,'In Days':np.max},margins=True)
 pivot_filtered_splitup = pd.pivot_table(filtered,index=['Salesman','Beat Name','party','Bill Number'],values=['O/S Amount','In Days'],aggfunc={'O/S Amount':np.sum,'In Days':np.max},margins=True)
 pivot_total_bills = pd.pivot_table(unfiltered,index=['Salesman','Beat Name','party'],values=['Bill Number'],aggfunc={'Bill Number':pd.Series.nunique},margins=True)
 pivot_filtered =pd.merge(pivot_total_bills,pivot_filtered,left_index=True,right_index=True)
 pivot_filtered=pivot_filtered[['Bill Number','In Days','O/S Amount']]
 with pd.ExcelWriter('outstandingreport.xlsx') as writer: 
    pivot_filtered.to_excel(writer, sheet_name='Summary')
    pivot_filtered_splitup.to_excel(writer, sheet_name='Detail') 
def main(date,days): #date can be string(yyy-mm-dd) or datetime
 if isinstance(date,str) :
     date=datetime.strptime(date,'%Y-%m-%d')
 day = date.strftime('%A').lower()
 driver = login(path)
 fpath = report_ajax(driver,"outstanding",{"fromd":datetime(2018,4,1).strftime("%Y-%m-%d"),
                                           "tod":date.strftime("%Y-%m-%d") },  make_download = True)
 salesmans = data_ajax(driver,"salesman",replaces={"url":"/rsunify/app/paginationController/getPopScreenData"}) #raw data
 salemans_id =  [salesman[1] for salesman in salesmans[0][1:] ]
 beats = []
 for salesmanid in  salemans_id :
   _beats = data_ajax(driver,"salesmanbeat",replaces={"url":"/rsunify/app/salesmanBeatLink/getSalesmanBeatLinkMappings",'salesmanid':str(salesmanid)},content="form")
   print(_beats)
   beats += [beat["beatName"] for beat in _beats if beat[day+'Linked'] == '1' ]
 interpret(fpath,beats,days)
 with open("config.txt") as f : 
     config = eval(f.read())
     if int(config['autoemail']) == 1 :
      try :
         mail.send(date,config['email'])
         print('email sent')
      except :
         print("mail failed")




       





       

