
import win32com.client
path = "D:\\"
filename ="LeverEDGE_41A392_Credit Locking_2022022506104210421042.xlsx"

shops ={'CHITRA STORE-F':1}
o = win32com.client.gencache.EnsureDispatch("Excel.Application")
o.WindowState = win32com.client.constants.xlMinimized
o.Visible = 1

wb = o.Workbooks.Open(path+filename)
