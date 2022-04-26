import pandas as pd
def z(x,data) :
    #print(x,data)
    return data[x]
def process(df,data) :
    f=open('eway\\vehicle.txt')
    vehname=eval(f.read())
    f.close()
    df['Vehicle No']=df['Document Number'].apply(lambda x: z(x,data))
    df['Trans Name']=df['Vehicle No'].apply(lambda x:vehname[x])
    df['Distance level(Km)']=3
    print(df[df['Buyer GSTIN'].isna()])
    df = df[df['Buyer GSTIN'].notna()]
    print(set(list(df['Buyer GSTIN'])))
    return df
