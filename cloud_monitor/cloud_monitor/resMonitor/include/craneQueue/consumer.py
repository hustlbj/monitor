import pika
import json
import uuid
from publisher import DirectPublisher
from common import TimeOutError

class DirectConsumer(object):
    """A direct conusmer of rabbitmq

    The consumer will never call "start_consuming()" interface,
    it is just for RPC publisher to get the response meessage
    """

    def __init__(self,exchange,timeout=30):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

        channel = self.connection.channel()

        channel.exchange_declare(exchange = exchange,
                                type = 'direct')

        rlt = channel.queue_declare(exclusive = True)
        self.direct_queue = rlt.method.queue

        self._uuid = str(uuid.uuid4())

    
        channel.queue_bind(exchange = exchange,
                            queue = self.direct_queue,
                            routing_key = self._uuid)

        self.response = None
        channel.basic_consume(self.callback,no_ack = True,queue = self.direct_queue)

        self.timeout = timeout

    def callback(self, ch, method, props, body):
        if props.correlation_id == self.corr_id:
            self.response = body

    def set_corr_id(self,corr_id):
        self.corr_id = corr_id

    def process_data(self):
        def _process_callback():            
            raise TimeOutError(func="process_data")

        timeout_id = self.connection.add_timeout(self.timeout,_process_callback)

        try:
            while self.response is None:
                self.connection.process_data_events()
        except TimeOutError,tm:            
            self.response = json.dumps([False,tm.__str__()])

        self.connection.remove_timeout(timeout_id)

        rlt = self.response
        self.response = None

        return rlt

    def queue(self):
        return self.direct_queue

    def identity(self):
        return self._uuid

class TopicConsumer(object):
    """A topic consumer of rabbitmq

    The consumer is the server agent for cast calls
    """

    def __init__(self,exchange,topic,_callback):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))

        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=exchange,
                                        type='topic')

        rlt = self.channel.queue_declare(exclusive=True)
        self.topic_queue = rlt.method.queue

        self.channel.queue_bind(exchange=exchange,
                                queue=self.topic_queue,
                                routing_key=topic)

        self._callback = _callback
        self.channel.basic_consume(self.callback,queue=self.topic_queue)

    def callback(self,ch,method,props,body):
        try:
            self._callback(body)
        except Exception:
            pass

    def consume(self):
        self.channel.start_consuming()

    def cancel(self):
        self.channel.stop_consuming()
        self.connection.close()
    
    def close(self):
        self.connection.close()



class RPCConsumer(TopicConsumer):
    """A topic consumer of rabbitmq

    The consumer will call "start_consuming" interface ,
    as a server to listen and accept the message
    """
    def __init__(self,exchange,topic,_callback,direct_publisher):
        super(RPCConsumer,self).__init__(exchange,topic,_callback)
        
        self.direct_publisher = direct_publisher

    def callback(self,ch,method,props,body):
        try:
            response = self._callback(body)
        except Exception,e:
            response = json.dumps([False,e.__str__()])

        if response:            
            self.direct_publisher.publish(msg=response,corr_id=props.correlation_id)

        self.channel.basic_ack(delivery_tag=method.delivery_tag)
