from consumer import DirectConsumer
from publisher import TopicPublisher,RPCPublisher
from logger import Logger
from common import NotImplementedError
import uuid
import json
import time
import threading

"""
    The invoker is in mul-thread environment.
    So what we should do is to protect the shared resource:
        rpc_publisher
        topic_publisher
"""

class BasicProxy(object):
    def __init__(self,conf,service,host='localhost'):
        self.service = service
        self._mutex = threading.Lock()
        
        self._logger = Logger(logger_file=self.__class__.__name__,
                            file_dir=self.__class__.__name__)
    @staticmethod
    def make_msg(method,**kwargs):
        return json.dumps({'method':method,'args':kwargs}) 

    def call(self,message,topic,timeout = -1):
        raise NotImplementedError(func = 'call')

    def cast(self,message,topic):
        raise NotImplementedError(func = 'cast')

class RPCProxy(BasicProxy):
    def __init__(self,conf,service,host='localhost'):
        super(RPCProxy,self).__init__(conf,service,host) 
        
        self.rpc_publisher = RPCPublisher(exchange=conf["RPC_EXCHANGE"],host=host)
        self._direct_exchange = conf["DIRECT_EXCHANGE"]

    def call(self,message,topic,timeout = -1):
        call_topic = "rpc.%s.%s" %(self.service,topic)

        corr_id = str(uuid.uuid4())
        if timeout >= 0:
            direct_consumer = DirectConsumer(exchange=self._direct_exchange,timeout=timeout)
        else:
            direct_consumer = DirectConsumer(exchange=self._direct_exchange)
        
        direct_consumer.set_corr_id(corr_id)

        self._mutex.acquire()
        self.rpc_publisher.publish(msg=message,
                                    corr_id=corr_id,
                                    reply_to=direct_consumer.queue(),
                                    topic=call_topic,
                                    identity=direct_consumer.identity())
        self._logger.logging(msg=message,
                            identity=direct_consumer.identity())

        self._mutex.release()

        return direct_consumer.process_data()

class TOPICProxy(BasicProxy):

    def __init__(self,conf,service,host='localhost'):
        super(TOPICProxy,self).__init__(conf,service,host)
        self.topic_publisher = TopicPublisher(exchange=conf["TOPIC_EXCHANGE"],host=host)


    def cast(self,message,topic):
        """call a remote method, and do not waiting for a result

        :param 'message' : Its type is str, create by 'make_msg()'
        :param 'topic' : Its the name of the method
        """
        cast_topic ="topic.%s.%s" % (self.service,topic)

        self._mutex.acquire()
        self.topic_publisher.publish(msg=message,topic=cast_topic)
        self._logger.logging(msg=message)
        self._mutex.release()
 
class Proxy(BasicProxy):
    """A helper class for clients.

    This class is a wrapper around a client API.
    This is to be used as a base class for a class that implements the client side of an rpc API.
    """

    def __init__(self,conf,service,host='localhost'):
        """Initialize an Proxy

        :param 'conf' : It is a dict with the keys('RPC_EXCHANGE','TOPIC_EXCHANGE','DIRECT_EXCHANGE') which
                        is used to define exchanges.
        :param 'service' : It is a name of a service , "iaas" for example.
        :param 'host'   :Server to connect
        """
        super(Proxy,self).__init__(conf,service,host)

        self.rpc_publisher = RPCPublisher(exchange=conf["RPC_EXCHANGE"],host=host)
        self.topic_publisher = TopicPublisher(exchange=conf["TOPIC_EXCHANGE"],host=host)
        
        self._direct_exchange = conf["DIRECT_EXCHANGE"]


    @staticmethod
    def make_msg(method,**kwargs): 
        """convert Request to string in json

        :param 'method' : It is a name of method to ask for, its type is str.
        :param 'kwargs' : It is the paramters for the 'method'

        :returns : The return value is the str
        """
        return json.dumps({'method':method,'args':kwargs})

    def call(self,message,topic,timeout = -1):
        """ RPC call a remote method, and waiting for result

        :param 'message' : Its type is str , created by 'make_msg()
        :param 'topic' :  Its the name of the method

        :returns :  value of remote method
        """
    
        call_topic = "rpc.%s.%s" %(self.service,topic)

        corr_id = str(uuid.uuid4())
        if timeout >= 0:
            direct_consumer = DirectConsumer(exchange=self._direct_exchange,timeout=timeout)
        else:
            direct_consumer = DirectConsumer(exchange=self._direct_exchange)
        
        direct_consumer.set_corr_id(corr_id)

        self._mutex.acquire()
        self.rpc_publisher.publish(msg=message,
                                    corr_id=corr_id,
                                    reply_to=direct_consumer.queue(),
                                    topic=call_topic,
                                    identity=direct_consumer.identity())
        self._logger.logging(msg=message,
                            identity=direct_consumer.identity())

        self._mutex.release()

        return direct_consumer.process_data()

    def cast(self,message,topic):
        """call a remote method, and do not waiting for a result

        :param 'message' : Its type is str, create by 'make_msg()'
        :param 'topic' : Its the name of the method
        """
        cast_topic ="topic.%s.%s" % (self.service,topic)

        self._mutex.acquire()
        self.topic_publisher.publish(msg=message,topic=cast_topic)
        self._logger.logging(msg=message)
        self._mutex.release()



if __name__=="__main__":
    conf={}
    conf["DIRECT_EXCHANGE"] = "call_direct_topic"
    conf["TOPIC_EXCHANGE"] = "service_call_topic"
    conf["RPC_EXCHANGE"] = "service_cast_topic"

    proxy = TOPICProxy(conf,"iaas")
    normal_req = {"method":"normal_func","args":{"value":0}}
    time_req = {"method":"time_func","args":{"value":0}}

    
    #rlt = proxy.call(json.dumps(time_req),time_req["method"])
    #print rlt
    rlt = proxy.cast(json.dumps(time_req),time_req["method"])
    print rlt
    
