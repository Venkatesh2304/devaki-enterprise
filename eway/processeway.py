import pandas as pd
def z(x,data) :
    #print(x,data)
    return data[x]
def process(df,data) :
    f=open('eway\\vehicle.txt')
    vehname=eval(f.read())
    f.close()
    df['Vehicle No']=df['Doc.No'].apply(lambda x: z(x,data))
    df['Trans Name']=df['Vehicle No'].apply(lambda x:vehname[x])
    df['To_Pin_code'],df['Distance level(Km)']=620008,3
    df=df[list(df.columns)[0:40]]
    return df
