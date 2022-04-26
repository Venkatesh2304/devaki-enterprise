import os 
def create(x) :
    try :
        os.makedir(x)
    except Exception as e:
        print(e)
f=open('GST:\\gst.txt')
desktopuser=eval(f.read())['desktopuser']
f.close()
folders=['D:\\dataprint','D:\\dataprint\\output','D:\\dataclaims','D:\\dataEWAY','D:\\EWAY','C:\\Users\\'+desktopuser+'\\Desktop\\GST']
for i in folders :
    create(i)
f=open('C:\\Users\\'+desktopuser+'\\Desktop\\GST\\log.txt','w+')
f.write("[]")
f.close()