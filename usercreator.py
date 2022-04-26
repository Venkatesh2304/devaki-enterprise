import pickle
user={'user':'devaki'}
f=open('config.bin','wb')
pickle.dump(user,f)
f.close()
