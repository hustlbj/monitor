import threading
from logger import Logger
import Queue
from publisher import DirectPublisher

'''
    This worker is used for call method.
'''
class RPCWorker(threading.Thread):
    _logger = None
    _mutex = threading.Lock()

    def __init__(self,tasks,exchange,destination='localhost',timeout=30,agent=None,**kwargs):
        threading.Thread.__init__(self,kwargs=kwargs)
        self.setDaemon(True)
        self.tasks = tasks
        self.exchange = exchange
        self.timeout = timeout
        self.destination = destination

        if RPCWorker._logger == None:
            logger_file = agent + "_" + self.__class__.__name__
            RPCWorker._logger = Logger(logger_file=logger_file,file_dir=agent)

        self.start()

    def run(self):
        while True:
            try:
                callback,identity,corr_id,delivery_tag,msg = self.tasks.get(timeout=self.timeout)
                if callback == -1:
                    break


                response = None
                try:
                    response = callback(msg)                    
                except Exception,e:
                    response = json.dumps([False,e.__str__()])


                if response:
                    direct_publisher = DirectPublisher(exchange = self.exchange,
                                                        routing_key = identity,
                                                        host=self.destination)

                    direct_publisher.publish(msg = response,
                                            corr_id = corr_id)

            except Queue.Empty:
                continue
            except Exception,e:
                break

'''
   This worker is used for cast method. 
'''

class TOPICWorker(threading.Thread):
    _logger = None

    _mutex = threading.Lock()

    def __init__(self,tasks, timeout=20,agent=None,**kwargs):
        threading.Thread.__init__(self,kwargs=kwargs)

        self.setDaemon(True)

        self.tasks = tasks

        self.timeout = timeout        
        if TOPICWorker._logger == None:
            logger_file = agent + "_" + self.__class__.__name__
            TOPICWorker._logger = Logger(logger_file=logger_file,file_dir=agent)

        self.start()

    def run(self):
        while True:
            try:
                    callback,msg,identity = self.tasks.get(timeout=self.timeout)


                    if callback == -1:
                        break

                    try:
                        callback(msg)
                        message = "callbacked"
                    except Exception,e:
                        message = e.__str__()

                    TOPICWorker._mutex.acquire()
                    TOPICWorker._logger.logging(msg = e.__str__ ,identity = identity)
                    TOPICWorker._mutex.release()
                        
            except Queue.Empty:
                continue
            except Exception,e:
                break

