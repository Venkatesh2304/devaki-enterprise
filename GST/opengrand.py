import win32com.client
import os

def opengrand(t) :
 o = win32com.client.Dispatch("Excel.Application")
 o.Visible = True
 o.DisplayAlerts = False

 if o.Workbooks.Count > 0:
    for i in range(1, o.Workbooks.Count+1):
            wb = o.Workbooks.Item(i)
            wb.close   
 filename =  t
 output =  t
 output=output.split('.')[0]+' 1.xls'
 wb = o.Workbooks.Open(filename)
#convert('C:\\Users\\new2018\\AppData\\Local\\Programs\\Python\\Python38-32\\company\\data\\14\\Ledger Report.xls')
