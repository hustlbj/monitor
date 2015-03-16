import pika
import uuid
import json

class DirectPublisher(object):
    """A direct publisher in rabbitmq
    """
    def __init__(self,exchange,routing_key,host='localhost'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))

        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=exchange,
                                        type='direct')

        self.exchange = exchange
        self.routing_key = routing_key

    def publish(self,msg,corr_id):
        self.channel.basic_publish(exchange=self.exchange,
                                    routing_key=self.routing_key,
                                    properties=pika.BasicProperties(correlation_id=corr_id),
                                    body=msg)

class TopicPublisher(object):
    """A topic publisher in rabbitmq
    """
    def __init__(self,exchange,host='localhost'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))

        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=exchange,
                                        type='topic')

        self.exchange = exchange        

    def publish(self,msg,topic):
        self.channel.basic_publish(exchange=self.exchange,
                                    routing_key=topic,
                                    body=msg)


class RPCPublisher(TopicPublisher):
    """A topic publish for RPC in rabbitmq
    """
    def __init__(self, exchange,host='localhost'):
        super(RPCPublisher, self).__init__(exchange,host)

    def publish(self,msg,corr_id,reply_to,topic, identity = None):
        if identity:
            msg = json.dumps([identity,msg])
                    
        self.channel.basic_publish(exchange=self.exchange,
                                    routing_key=topic,
                                    properties=pika.BasicProperties(reply_to=reply_to,
                                                                    correlation_id=corr_id),
                                    body=msg)
