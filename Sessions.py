import requests
import logging
from pprint import pformat
import inspect

func = lambda : True 
class Session(requests.Session) : 
    
    # def __getattribute__(self, __name: str) :
    #      value = super().__getattribute__(__name)   
    #     #  input( [ inspect.stack()[i][3] for i in range(len(inspect.stack())) ] )
    #      if hasattr(value,"__call__")  and type(value) == type(super().request) and (inspect.stack()[3][3] not in requests.Session.__dict__) and inspect.stack()[3][3] != "new_func" : 
    #         def new_func(*args,**kwargs) : 
    #             logging.debug(f"The function {__name} is started")
    #             return_val = value(*args,**kwargs)
    #             logging.debug(f"The function {__name} , returned {return_val}")
    #         input(  [ inspect.stack()[i][3] for i in range(len(inspect.stack())) ] )
    #         return new_func
    #      return super().__getattribute__(__name)
      
    def request(self,*args,**kwargs):
          res = super().request(*args,**kwargs)
          logging.debug(f"\nrequest : {args} {pformat(kwargs)} \n response : {res.url} {res.status_code} \n {pformat(res.text[:min(len(res.text),50)])}")
          return res 