#!/usr/bin/python
import json
import sys,os
import socket
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn

from constants import HOOK_SERVER_PORT
import net_attach



class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):pass

class IPServer(object):

    def __init__(self,port):
        self.register_client = []
        self.server = ThreadXMLRPCServer(("", int(port))) 

    def init_vm_ipv6(self,id,ipv6,ipv4):
        print id,ipv6,ipv4
        rl = net_attach.set_ipv6(str(id),ipv6)
        self._confirm(id,ipv4)
        return rl

    def notify_fail_vm(self,vmid):
        print vmid
        self._fail_notify(vmid)
        return True

    def register_confirm(self,port,host):
        server_address = (host,int(port))
        if not server_address in self.register_client:
            self.register_client.append(server_address)
        return server_address

    def _fail_notify(self,vmid):
        for address in self.register_client:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                message = json.dumps(['FAIL',str(vmid)])
                sock.connect(address)
                sock.send(message)
                rlt = sock.recv(1024)
                sock.close()
            except Exception,e:
                print str(e)
                self.register_client.remove(address)

    def _confirm(self,vmid,ipv4):
        print "register_client: ",self.register_client
        disabled_address = []
        for address in self.register_client:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                message = json.dumps(['CONFIRM',json.dumps([vmid,ipv4])])
                print "connect to",address,"with message: ",message
                sock.connect(address)
                sock.send(message)
                rlt = sock.recv(1024) #1024
                sock.close()
            except Exception,e:
                print str(e)
                disabled_address.append(address)
        for address in disabled_address:
            self.register_client.remove(address)
        

    def function_register(self):
        self.server.register_function(self.init_vm_ipv6)
        self.server.register_function(self.register_confirm)
        self.server.register_function(self.notify_fail_vm)

    def run(self):
        self.server.serve_forever()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print "IPServer.py or IPServer.py port"
        os._exit(1)
    elif len(sys.argv) == 2:
        port = len(sys.argv[1])
    else:
        port = HOOK_SERVER_PORT
    ip_server = IPServer(port)
    ip_server.function_register()
    ip_server.run()
