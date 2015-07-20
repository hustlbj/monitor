import sys, os, logging, commands
from SimpleXMLRPCServer import SimpleXMLRPCServer
try:
    from constants import NAT_OUTER_IP,NAT_INNER_IP,NAT_NETMASK,NAT_NIC,NAT_LOG_FILE,NAT_SERVER_IP,NAT_SERVER_PORT
except:
    NAT_OUTER_IP = ''
    NAT_INNERT_IP = ''  
    NAT_NETMASK = ''
    NAT_NIC = ''
    NAT_LOG_FILE = ''
    NAT_SERVER_IP = ''
    NAT_SERVER_PORT = -1

def initLogger():
    if NAT_LOG_FILE == '':
        return None

    logger = logging.getLogger()
    hdlr = logging.FileHandler(NAT_LOG_FILE)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger

logger = initLogger() 
serverIp = NAT_OUTER_IP
serverInnerIp = NAT_INNER_IP

def addNat(innerIp,portNum,innerPort):
    addInput = "iptables -A INPUT -d "+ innerIp +" -i "+NAT_NIC+" -p tcp -m tcp --dport "+innerPort+" -j ACCEPT"
    addPrerouting = "iptables -t nat -A PREROUTING -d "+ serverIp +" -p tcp -m tcp --dport "+ portNum +" -j DNAT --to-destination "+ innerIp +":"+innerPort+""
    addPostrouting = "iptables -t nat -A POSTROUTING -s "+NAT_NETMASK+" -d "+ innerIp +" -p tcp -m tcp --dport "+innerPort+" -j SNAT --to-source "+ serverInnerIp

    stat0, output0 = commands.getstatusoutput(addInput)
    stat1, output1 = commands.getstatusoutput(addPrerouting)
    stat2, output2 = commands.getstatusoutput(addPostrouting)
    stat3, output3 = commands.getstatusoutput("service iptables save")
    
    stats = (stat0, stat1, stat2, stat3)
    result = ','.join([str(x) for x in stats])
    message = "add mapping " + innerIp + " " + portNum + " to " + innerPort + " "+result
    logger.info(message)
    return True


def delNat(innerIp, portNum,innerPort):
    delInput = "iptables -D INPUT -d "+ innerIp +" -i "+NAT_NIC+" -p tcp -m tcp --dport "+innerPort+" -j ACCEPT"
    delPrerouting = "iptables -t nat -D PREROUTING -d "+ serverIp +" -p tcp -m tcp --dport "+ portNum +" -j DNAT --to-destination "+ innerIp +":"+innerPort+""
    delPostrouting = "iptables -t nat -D POSTROUTING -s "+NAT_NETMASK+" -d "+ innerIp +" -p tcp -m tcp --dport "+innerPort+" -j SNAT --to-source "+ serverInnerIp 
    stat0, output0 = commands.getstatusoutput(delInput)
    stat1, output1 = commands.getstatusoutput(delPrerouting)
    stat2, output2 = commands.getstatusoutput(delPostrouting)
    stat3, output3 = commands.getstatusoutput("service iptables save")
    stats = (stat0, stat1, stat2, stat3)
    result = ','.join([str(x) for x in stats])
    message = "del mapping " + innerIp + " " + portNum + " to " + innerPort +" "+result 
    logger.info(message)
    return True

def main():
    svr = SimpleXMLRPCServer((NAT_SERVER_IP, NAT_SERVER_PORT), allow_none=True, logRequests=False)  
    svr.register_function(addNat,"vm.net.port.set")
    svr.register_function(delNat,"vm.net.port.release")
    svr.serve_forever()  

if __name__ == "__main__":
    # do the UNIX double-fork magic, see Stevens' "Advanced 
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    if logger == None:
        print >> sys.stderr, "NAT Server Configuration INVALIDED"
        sys.exit(1)
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit first parent
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)

   # # decouple from parent environment
    os.chdir("/") 
    os.setsid() 
    os.umask(0) 

   # # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            logger.info("daemon pid:" + str(pid))
            print "Daemon PID %d" % pid 
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1) 

    #start the daemon main loop
    main() 


