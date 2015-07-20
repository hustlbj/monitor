#!/usr/bin/env python

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.server import TNonblockingServer


from crane.thrift import IaaSService
#from iaas_handler import  IaaSHandler
from eventtrace.import_utils import import_class
IaaSHandler = import_class('iaas_handler.IaaSHandler')
from craneQueue.service import Service
import sys, os

class IaaSAgent:

    def __init__(self,port,host = "localhost"):
	try:
	    self.iaas_handler = IaaSHandler()	 
	    self.processor = IaaSService.Processor(self.iaas_handler)

	    self.transport = TSocket.TServerSocket(host,port)
	    self.tfactory = TTransport.TBufferedTransportFactory()
            self.pfactory = TBinaryProtocol.TBinaryProtocolFactory()
           # self.server = TServer.TThreadPoolServer(self.processor, self.transport, self.tfactory, self.pfactory)
            self.server = TNonblockingServer.TNonblockingServer(self.processor, self.transport)
	except Exception,e:
	    self._fatal(e)

    def _fatal(self,e):
	print >> sys.stderr,"IaaSAgent FATAL ERROR:" , e.__str__()
        os._exit(1)

    def start_consume(self):
	try:
	    self.server.serve()
	except Exception,e:
	    self._fatal(e)

if __name__ == "__main__":
	port = 10113
	host = "localhost"
	if len(sys.argv) == 2:
		port = int(sys.argv[1])
	elif len(sys.argv) == 3:
		port = int(sys.argv[1])
		host = sys.argv[2] 
	else:
		#exit(1)
		pass
	iaas_service = IaaSAgent(port,host)
	iaas_service.start_consume()
#class IaaSServiceWrap(Service):
#    def __init__(self,
#                 pidfile ,
#                 stdin='/dev/null' ,
#                 stdout='/dev/null' ,
#                 stderr='/dev/null'):
#        stderr = '/usr/crane/package/cloud/iaas/stderr'
#        super(IaaSServiceWrap,self).__init__(pidfile,stdin,stdout,stderr)
#
#    def _run(self,iaas_service):
#	iaas_service.start_consume()
#
#
#if __name__ == '__main__':
#    if len(sys.argv) == 1:
#	op = "start"
#    elif len(sys.argv) == 2:
#        op = sys.argv[1]
#    else:
#	print >> sys.stderr,"args invalid"
#        sys.exit(1)
#
#    file = "/usr/crane/package/cloud/iaas/IaaSAgent.pid"
#
#    try:
#        service = IaaSServiceWrap(file)
#    except Exception,e:
#	print >> sys.stderr,"Servce Create FATAL ERROR", e.__str__()
#        os._exit(1)
#
#    if op == "start":
#	iaas_service = IaaSAgent(10113)
#	service.start(iaas_service)
#    elif op == "stop":
#	service.stop()
#    else:
#	print >> sys.stderr, "NO Such Command" 
