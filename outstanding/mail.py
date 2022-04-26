import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from os.path import basename
from email.mime.text import MIMEText
import pandas as pd
import datetime
def send(date,reciever) :
 # content
 msg = MIMEMultipart()
 sender = "jamkutsfinal@gmail.com"
 password = "Venkatesh2304"
 text = " Outstanding Report , " + date.strftime('%d/%m/%Y') +' or '+date.strftime('%d-%m-%Y')

# action
 msg['subject'] = 'Outstanding report'   
 msg['from'] = sender
 msg['to'] = reciever
 msg.attach(MIMEText(text))
 files=['outstanding\\outstandingreport.xlsx']
 for f in files or []:
  with open(f, "rb") as fil:
      part = MIMEApplication(
                fil.read(),
                Name='outstanding '+date.strftime('%d-%m-%Y')+'.xlsx'
           )
        # After the file is closed
  part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
 msg.attach(part)
 with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(sender,password)
    smtp.send_message(msg)
    smtp.close()

