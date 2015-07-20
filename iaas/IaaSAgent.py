#!/usr/bin/env python
"""
Created on Sep 4,2012

@author LiYC
"""

from craneQueue.agent import _main ,RPCAgent, conf
#from IaaSOperation import IaaSOperation
from common.exception import RpcDownException, RpcErrorException

from eventtrace.import_utils import import_class
IaaSOperation = import_class('IaaSOperation.IaaSOperation')

class IaaSAgent(RPCAgent):
    """
    Serve Side of IaaS API
    """
    
    def __init__(self,conf,service):
        """Initialize an iaas api proxy
        
        :param 'conf': It is a dict with the keys('RPC_EXCHANGE','TOPIC_EXCHANGE','DIRECT_EXCHANGE') 
        is used to define exchanges
        :param 'service' : It is 'iaas'
        """
        
        super(IaaSAgent,self).__init__(conf,service)
        self.iaasOperation = IaaSOperation()

    def rpc_callback(self,message):
        """RPC call, Realiszed by the class that implements the server side
    
        :param 'message' : Its a string of requet, '{"method":"getVmpoolInfo","args":{"user":"test"}}', for example.
        Using the self.func_obtain(module,method) to get the function object.
        :returns : return the result to the rpc client that is waiting for.
        """
        msg = self.msg_make(message)
	print "RPC: MSG", msg
        try:   
            func = self.func_obtain(self.iaasOperation,msg["method"])
	    print "FUNC OBTAIN END"
            print "Func:"+str(func)
            rlt =  func(**msg["args"])
	    print "TRY END"
        except (RpcDownException,RpcErrorException) as err:
            return self.make_msg([False, str(err)])
        except KeyError as err:
            return self.make_msg([False, str(err)])
	except Exception,err :
            return self.make_msg([False, str(err)])
        return self.make_msg(rlt)


    '''It will never be invoked.
    '''
    def topic_callback(self,message):
        """Normal call, Realiszed by teh class that implements the server side

        :param 'message' : It is the same to 'rpc_callback()' parameter 'message'
        """
        msg = self.msg_make(message)
        try:
            func = self.func_obtain(self.iaasOperation,msg["method"])
            rlt =  func(**msg["args"])
        except (RpcDownException,RpcErrorException) as err:
            return self.make_msg([False, str(err)])
        except KeyError as err:
            return self.make_msg([False, str(err)])
        return self.make_msg[True, "Put Into The Queue!"]

if __name__=="__main__":
    _main(conf,IaaSAgent,'iaas_api')
    #iaas_api = IaaSAgent(conf,'iaas_api')

    #iaas_api.start_consuming()
