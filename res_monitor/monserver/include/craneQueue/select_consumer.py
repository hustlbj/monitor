import pika
import json
from publisher import DirectPublisher
from common import TimeOutError
import threading
import time
from worker import RPCWorker,TOPICWorker
from logger import Logger
import Queue
import uuid
import os

class STopicConsumer(object):
    """A Topic consumer with selectconnection
    """
    def __init__(self, exchange, topic, _callback,num_thread = 5, url="localhost",agent = None):
        self._connection = None
        self._channel = None
        self._queue = None

        self._exchange = exchange
        self._topic = topic
        self._callback = _callback
        self._url = url

        self._num_thread = num_thread
        self._workers = []
        self._tasks = Queue.Queue()

        self._mutex = threading.Lock()

        if not agent:
            agent = ''

        self._agent = agent

        self._logger = Logger(logger_file=agent+"_"+self.__class__.__name__,
                            file_dir=agent)

    def _create_workers(self):
        for i in range(self._num_thread):
            worker = TOPICWorker(tasks=self._tasks,agent=self._agent)
            self._workers.append(worker)

    def connect(self):
        parameters = pika.ConnectionParameters(host = self._url)
        return pika.SelectConnection(parameters,self.on_connection)

    def on_connection(self, unused_connection):
        self.open_channel()

    def open_channel(self):        
        self._connection.channel(on_open_callback = self.on_channel)

    def on_channel(self,channel):
        self._channel = channel
        self.setup_exchange(self._exchange)

    def setup_exchange(self,exchange):
        self._channel.exchange_declare(callback = self.on_exchange,
                                        exchange = exchange,
                                        type = 'topic')

    def on_exchange(self,unused_frame):
        self.setup_queue()

    def setup_queue(self):
        self._channel.queue_declare(self.on_queue,
                                    exclusive = True)

    def on_queue(self, method_frame):
        self._queue = method_frame.method.queue
        self._channel.queue_bind(callback = self.on_bind,
                                    queue = self._queue,
                                    exchange = self._exchange,
                                    routing_key = self._topic)

        self._create_workers()

    def on_bind(self, unused_frame):
        self.start_consuming()

    def start_consuming(self):
        self._channel.basic_consume(self.callback,
                                    self._queue)

    def callback(self,channel, method, properties, body):
        identity = str(uuid.uuid4())
        self._logger.logging(msg = body,identity=identity)
        self._tasks.put((self._callback,body,identity))


    def consume(self):
        try:
            self._connection = self.connect()
        except Exception,e:
            print str(e)
            os._exit(1)
        
        try:
            self._connection.ioloop.start()
        except Exception,e:
            self._connection.ioloop.start()

    def stop(self):
        self._logger.close()
        self.stop_consuming()

    def stop_consuming(self):
        self._channel.close()
        self._connection.close()
        for i in range(self._num_thread):
            self._tasks.put((-1,None))

        for each in self._workers:
            each.join()

        


class SRPCConsumer(STopicConsumer):
    """A Topic consumer witch selectConnection
    """
    def __init__(self, exchange, topic, _callback, direct_exchange,num_thread=5,url='localhost',agent=None,destination='localhost'):
        super(SRPCConsumer,self).__init__(exchange,topic,_callback,num_thread,url,agent)

        self._direct_exchange = direct_exchange
        self.destination = destination
       

    def _create_workers(self):
        for i in range(self._num_thread):
            worker = RPCWorker(tasks = self._tasks,destination=self.destination ,exchange = self._direct_exchange,agent = self._agent)
            self._workers.append(worker)
        

    def callback(self,channel, method, properties, body):
        identity = None
        try:
            msg = json.loads(body)
            if(type(msg) == list):
                identity = msg[0]
                body = msg[1]
                self._logger.logging(msg = body,
                                    identity = identity)
        except Exception,e:
            pass
        self._tasks.put((self._callback,identity,properties.correlation_id,method.delivery_tag,body))
        self._channel.basic_ack(delivery_tag = method.delivery_tag)


    def stop_consuming(self):
        self._channel.close()
        self._connection.close()
        for i in range(self._num_thread):
            self._tasks.put((-1,None,None,None,None))

        for each in self._workers:
            each.join()

