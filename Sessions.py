import requests
import logging
from pprint import pformat

func = lambda : True 
class Session(requests.Session) : 
          
    def request(self,*args,**kwargs):
          res = super().request(*args,**kwargs)
          logging.debug(f"\nrequest : {args} {pformat(kwargs)} \n response : {res.url} {res.status_code} \n {pformat(res.text[:min(len(res.text),50)])}")
          return res 