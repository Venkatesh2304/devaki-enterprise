import pandas as pd
def z(x,data) :
  return data[x]  
def process_eway(df,data={} , vehicle = False ) :
    with open('eway\\vehicle.txt') as f : 
       vehname=eval(f.read())
    if vehicle == False :   
       df['Vehicle No']=df['Doc.No'].apply(lambda x: z(x,data))
    else : 
       df['Vehicle No'] =  vehicle
    df['Trans Name']=df['Vehicle No'].apply(lambda x:vehname[x])
    df['To_Pin_code'],df['Distance level(Km)']=620008,3
    df=df[list(df.columns)[0:40]]
    return df
def process_einvoice(df, data ={} , vehicle = False) :
    with open('eway\\vehicle.txt') as f : 
       vehname=eval(f.read())
    if vehicle == False  :   
       df['Vehicle No']=df['Document Number'].apply(lambda x: z(x,data))
    else : 
       df['Vehicle No'] =  vehicle
    df['Trans Name']=df['Vehicle No'].apply(lambda x:vehname[x])
    df["Shipping Location"]  = "TRICHY"
    df["Buyer Location"]  = "TRICHY"
    df["Buyer Pin Code"] = df["Buyer Pin Code"].apply(lambda pin : 620008 if (pin is None or pin!=pin) else  pin )
    df["Shipping Pin Code"] = df["Shipping Pin Code"].apply(lambda pin : 620008 if (pin is None or pin!=pin) else  pin )
    df['Distance level(Km)']=3
    df = df[df['Buyer GSTIN'].notna()]
    return df
