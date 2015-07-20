#!/usr/bin/python
from  constants import HOOK_SERVER_PORT,HOOK_SERVER_IP

import xmlrpclib
import sys
if __name__ == "__main__":
    URL = "http://%s:%d/"%(HOOK_SERVER_IP, HOOK_SERVER_PORT)
    server = xmlrpclib.ServerProxy(URL)
    server.notify_fail_vm(sys.argv[1])
