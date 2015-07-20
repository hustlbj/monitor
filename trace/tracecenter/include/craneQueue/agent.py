from consumer import TopicConsumer,RPCConsumer
from select_consumer import STopicConsumer,SRPCConsumer
from publisher import DirectPublisher
from common import NotImplementedError
from service import Service
from logger import QUEUE_LOG_DIR 
import json
import threading
import os
import time
import sys
import os
import signal

class BasicAgent(object):
    def __init__(self,conf,service,host='localhost'):
        self.topic_routing = "topic.%s.#"
        self.rpc_routing = "rpc.%s.#"

    @staticmethod
    def msg_make(message):
        return json.loads(message)

    @staticmethod
    def make_msg(message):
        return json.dumps(message)

    @staticmethod
    def func_obtain(module,method):
        """Get the function object of the method of module(object)

        :param 'module' : It is a name of module or object ,its type is not a string
        :param 'method' : It is the name of a function ,it type is string
        """
        func = None
        try:
            func = getattr(module,method)
        except Exception,e:
            pass

        return func



    def close(self):
        raise NotImplementedError(func="close")

    def start_consuming(self):
        raise NotImplementedError(func="start_consuming")

    def sigterm_handler(self,signum,frame):
        if signum == signal.SIGTERM:
            print "pid: ",os.getpid()
            os.kill(0,signal.SIGTERM)
            os._exit(0)    


class RPCAgent(BasicAgent):
   
    def __init__(self,conf,service,host='localhost',destination='localhost'):
        super(RPCAgent,self).__init__(conf,service,host)

        self.rpc_consumer = SRPCConsumer(exchange=conf["RPC_EXCHANGE"],
                                        topic=self.rpc_routing%service,
                                        _callback=self.rpc_callback,
                                        direct_exchange = conf["DIRECT_EXCHANGE"],
                                        url = host,
                                        agent=self.__class__.__name__,
                                        destination=destination)


    def start_consuming(self):
        print "RPCAgent start"
        try:
            self.rpc_consumer.consume()
        except Exception,e:
            print str(e)
            self.rpc_consumer.stop()

    def close(self):
        self.rpc_consumer.stop()

    def rpc_callback(self,message):
        raise NotImplementedError(func="rpc_callback")


class TOPICAgent(BasicAgent):

    def __init__(self,conf,service,host='localhost'):
        super(TOPICAgent,self).__init__(conf,service,host)

        self.topic_consumer = STopicConsumer(exchange=conf["TOPIC_EXCHANGE"],
                                            topic=self.topic_routing%service,
                                            _callback=self.topic_callback,
                                            url = host,
                                            agent=self.__class__.__name__)
    def start_consuming(self):
        print "TOPICAgent start"
        try:
            self.topic_consumer.consume()
        except Exception,e:
            print str(e)
            self.topic_consumer.stop()

    def close(self):
        self.topic_consumer.stop()

    def topic_callback(self,message):
        raise NotImplementedError(func="topic_callback")


class Agent(BasicAgent):
    """A help class for servers

    This class is a wrapper around a server API.
    This is to be used as a base class for a class that implements the server side of an rpc API.
    The 'rpc_callback()' and 'topic_callback()' must be realiszed.
    """
    def __init__(self,conf,service,host='localhost',destination = 'localhost'):
        """Initialize an Agent

        :param 'conf' : It is a dict with the keys('RPC_EXCHANGE','TOPIC_EXCHANGE','DIRECT_EXCHANGE') which
                        is used to define exchanges.
        :param 'service' : It is a name of a service , "iaas" for example.
        """
        super(Agent,self).__init__(conf,service,host)

        self.threads = []
        self.topic_consumer = STopicConsumer(exchange=conf["TOPIC_EXCHANGE"],
                                            topic=self.topic_routing%service,
                                            _callback=self.topic_callback,
                                            url = host,
                                            agent=self.__class__.__name__)
        self.rpc_consumer = SRPCConsumer(exchange=conf["RPC_EXCHANGE"],
                                        topic=self.rpc_routing%service,
                                        _callback=self.rpc_callback,
                                        direct_exchange = conf["DIRECT_EXCHANGE"],
                                        url = host,
                                        agent=self.__class__.__name__,
                                        destination=destination)



    def rpc_callback(self,message):
        raise NotImplementedError(func="rpc_callback")

    def topic_callback(self,message):
        raise NotImplementedError(func="topic_callback")

    @staticmethod
    def thread_main(consumer):
        try:            
            consumer.consume()
        except KeyboardInterrupt:
            consumer.stop()


    def close(self):
        self.rpc_consumer.stop()
        self.topic_consumer.stop()
        for each in self.threads:
            each.join()        

    def start_consuming(self):
        print "start_consuming"
        self.threads.append(threading.Thread(target=self.thread_main,args=(self.rpc_consumer,)))
        self.threads.append(threading.Thread(target=self.thread_main,args=(self.topic_consumer,)))

        for each in self.threads:
            each.start()

def _main(conf,Agent,topic):
    if len(sys.argv) == 1:
        op = "start"
    elif len(sys.argv) == 2:
        op = sys.argv[1]
    else:
        sys.exit(1)

    file = QUEUE_LOG_DIR + "/" + Agent.__name__ + ".pid"
    service = Service(file)

    agent = Agent(conf,topic)

    if op == "start":        
        service.start(agent)
    elif op == "stop":
        service.stop()
    elif op == "restart":            
        service.restart(agent)
        

class Test(TOPICAgent):
    def __init__(self,conf,service,host='localhost',destination='localhost'):
        super(Test,self).__init__(conf,service,host)#,destination)

    def rpc_callback(self,message):
        msg = self.msg_make(message)
        print msg
        if msg['method'] == 'normal_func':
            return self.normal_func(**msg["args"])
        elif msg['method'] == 'time_func':
            return self.time_func(**msg["args"])
        else: 
            return "RPC_CALLBACK RETURN"

    def topic_callback(self,message):
        print "[TOPIC_CALLBACK]: ",self.msg_make(message)

    def normal_func(self,value):
        print value
        return "value"+str(value)

    def time_func(self,value):
        print value
        time.sleep(2)
        return "value"+str(value)

if __name__=="__main__":
    conf={}
    conf["DIRECT_EXCHANGE"] = "call_direct_topic"
    conf["TOPIC_EXCHANGE"] = "service_call_topic"
    conf["RPC_EXCHANGE"] = "service_cast_topic"

    #agent = Test(conf,'iaas')
    #agent.start_consuming()
    _main(conf,Test,"iaas")
