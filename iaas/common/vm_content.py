'''
Created on 2013-3-23

@author: Wuxl
'''
import os

if os.getenv('ONE_LOCATION'):
    ONE_LOCATION = os.getenv('ONE_LOCATION')
else:
    ONE_LOCATION = ""

if os.getenv('DOUBLE_NIC'):
    SINGLE_NIC = False
else:
    SINGLE_NIC = True
CONF_DIR = "/tmp/cloud"
MODE="qcow2"
ONE_DATA=ONE_LOCATION + "/var/crane.data"
ONE_RPC_SERVER = "localhost"

ONE_RPC_PORT = 2633
ONE_RPC_URI = "http://%s:%i/RPC2" % (ONE_RPC_SERVER,ONE_RPC_PORT)

KEY_DIR = ONE_LOCATION + "/share/scripts/userkeys"

VM_RANK = "FREEMEMORY"

VM_GRAPHICS_TYPE = "vnc"
VM_GRAPHICS_LISTEN = "0.0.0.0"


VM_DISK_DRIVER = "qcow2"
VM_DISK_MODE = "qcow2"
VM_DISK_TARGET = "vda"

VM_OS_ARCH = "x86_64"

BASIC_VIRTUAL_NET = "LAN"
ATTACH_VIRTUAL_NET = "XLAN"

NETMASK = "255.255.0.0"
GATEWAY = "11.11.0.71"

CD_TARGET = "vdb"

KEY = "id_dsa"

class BasicVirtualMachine(object):
    BASIC_REQUIRE = "FREEMEMORY > %(memory)i"
    
    def __init__(self):
        self.virtual_machine = {
                            "memory"    :           -1,
                            "vcpu"      :           -1,
                            "os"        :           None,
                            "graphics"  :           None,
                            "disk"      :           None,
                            "nic"       :           [],
                            "context"   :           {
                                                        "ip_public"     :   None,
                                                        "netmask"       :   None,
                                                        "one_vmid"      :   "$VMID",
                                                        "crane_user"    :   None,
                                                        "gateway"       :   None,
                                                        "target"        :   None
                                                    },
                            "requirements"          :       None,
                            "rank"      :           None
        }
        
    
    def create(self,memory,vcpu,user):
        self.virtual_machine["memory"]  = memory
        self.virtual_machine["vcpu"]    = vcpu
        self.virtual_machine["context"]["crane_user"] = user
    

    
    def add_requirement(self,hostname=None):        
        req = {"memory":int(self.virtual_machine["memory"])*1024}
        requirements = BasicVirtualMachine.BASIC_REQUIRE
        
        if hostname:
            requirements = requirements+ " & HOSTNAME = \\\"%(hostname)s\\\""
            req["hostname"] = hostname 
        
        self.virtual_machine["requirements"] = "\""+requirements % req+"\""
    
    def add_rank(self,rank = VM_RANK):
        self.virtual_machine["rank"] = rank
        
    def add_graphics(self,graphics_type = VM_GRAPHICS_TYPE,listen = VM_GRAPHICS_LISTEN ):
        graphics = "type = \"%s\" , listen = \"%s\""
        self.virtual_machine["graphics"] = graphics % (graphics_type,listen)
    
    def add_disk(self, image ,driver = VM_DISK_DRIVER,mode = VM_DISK_MODE, disk_target = VM_DISK_TARGET):
        if image.find('/') != -1:
            disk = "source = \"%s\""
        else:
            disk = "image = \"%s\""
        disk = disk + ", driver = \"%s\", mode = \"%s\", target = \"%s\""            
        
        self.virtual_machine["disk"] = disk % (image,driver,mode,disk_target)
    
    def add_os(self,arch = VM_OS_ARCH):
        os = "ARCH = \"%s\""
        self.virtual_machine["os"] = os % arch
    
    def add_basic_net(self,basic_net = BASIC_VIRTUAL_NET):
        net = " NETWORK = \"%s\""
        ip_public = "$NIC[IP, NETWORK = \\\"%s\\\"]"
        
        net = net % basic_net
        ip_public = ip_public% basic_net
                    
        self.virtual_machine["nic"].append(net)
        self.virtual_machine["context"]["ip_public"] = ip_public
    
    def add_net_setting(self,netmask = NETMASK, gateway = GATEWAY):
        self.virtual_machine["context"]["gateway"] = gateway
        self.virtual_machine["context"]["netmask"] = netmask
    
    def add_target(self, target = CD_TARGET):
        self.virtual_machine["context"]["target"] = target
    
    def add_context_option(self,key,value):
        self.virtual_machine["context"][key] = value
    
    def add_option(self,key,value):
        self.virtual_machine[key] = value
    
    def to_content(self):
        content = ""
        line = "%s=%s\n"
        bracketline = "%s=[%s]\n"
        stringline = "%s=\"%s\",\n"
        
        for each in self.virtual_machine:
            if each == 'os' or each == 'graphics' or each == 'disk':
                content = content + bracketline %(each, self.virtual_machine[each])
            elif each == 'nic':
                for each_nic in self.virtual_machine["nic"]:
                    content = content + bracketline %("nic", each_nic)
            elif each == 'context':
                context = ""
                for each_item in self.virtual_machine['context']:
                    context = context + stringline%(each_item,self.virtual_machine['context'][each_item])                                
                context =  context[0:context.find(',',-2)]                
                content = content + bracketline %('context',context)
                
                
            else:
                content = content + line%(each,self.virtual_machine[each])
        return content
                    
    

class DoubleNicVirutalMachine(BasicVirtualMachine):    
    
    def __init__(self):
        BasicVirtualMachine.__init__(self)
    
    def add_net(self,basic_net = BASIC_VIRTUAL_NET, attach_net = ATTACH_VIRTUAL_NET):
        BasicVirtualMachine.add_basic_net(self,basic_net)
        
        net = "NETWORK = \"%s\""        
        self.virtual_machine["nic"].append(net % attach_net)
        



class WindowsVirtualMachine(object):
    
    def __init__(self,basic = True):
        print "VirtualMachine"
        self.vm = None
        if basic:
            self.vm = BasicVirtualMachine()
            print "Basic"
        else:
            self.vm = DoubleNicVirutalMachine()
            print "Double"
        
        self.basic = basic
    
    def _set_disk(self,hvm):
        if not (hvm.has_key("driver") and hvm.has_key("mode") and hvm.has_key("disk_target")):
            hvm["driver"] = 'qcow2'
            hvm["mode"] = 'qcow2'
            hvm["disk_target"] = 'hda'
        
        if not (hvm.has_key("target")):
            hvm["target"] = 'hdb'
        
    
    def _create(self,hvm):
        if not (hvm.has_key("memory") and hvm.has_key("vcpu") and hvm.has_key("user") and hvm.has_key("img")):
            raise Exception("hvm invalid")
        
        self.vm.create(hvm["memory"], hvm["vcpu"], hvm["user"])
        
        if hvm.has_key("flag"):
            self.vm.add_option("flag", hvm["flag"])

        if hvm.has_key("node"):
            self.vm.add_requirement(hvm["node"])
        else:
            self.vm.add_requirement()
        
        if hvm.has_key("rank"):
            self.vm.add_rank(hvm["rank"])
        else:
            self.vm.add_rank()
        
        if hvm.has_key("arch"):
            self.vm.add_os(hvm["arch"])
        else:
            self.vm.add_os()
        
        if hvm.has_key("graphics_type") and hvm.has_key("listen"):
            self.vm.add_graphics(hvm["graphics_type"], hvm["listen"])
        else:
            self.vm.add_graphics()
        
        
        if hvm.has_key("driver") and hvm.has_key("mode") and hvm.has_key("disk_target"):
            self.vm.add_disk(hvm["img"], hvm["driver"], hvm["mode"], hvm["disk_target"])
        else:
            self.vm.add_disk(hvm["img"])
        
        self.vm.add_net_setting()
        
        if hvm.has_key("target"):
            self.vm.add_target(hvm["target"])
        else:
            self.vm.add_target()
        
        if self.basic == False:            
            self.vm.add_net()
        else:
            self.vm.add_basic_net()

    
    def create(self,hvm):
        self._set_disk(hvm)                    
        self._create(hvm)
        
        
        
    
            
        

class LinuxVirtualMachine(WindowsVirtualMachine):
    context = {
                    "root_pubkey"           :       "id_rsa.pub",
                    "nameserver"            :       "resolv.conf",
                    "files"                 :       "/etc/resolv.conf    "
                                                    "/usr/crane/package/conf/webpaas.conf    "
                                                    "/usr/crane/package/monitor/monagent/    "
                                                    "/srv/one/share/scripts/init.sh    "
                                                    "/srv/one/share/scripts/ipv6.py    "
                                                    "/srv/one/share/scripts/run_remote_command.py    "
                                                    "/home/crane/.ssh/id_rsa.pub    "
                                                    "/etc/resolv.conf    "              
                                                                                                                            
    }
    
    def __init__(self, basic = True):
        WindowsVirtualMachine.__init__(self, basic)        
        
        for key in LinuxVirtualMachine.context:
            self.vm.add_context_option(key, LinuxVirtualMachine.context[key])
    
    def _set_disk(self,hvm):
        if not (hvm.has_key("driver") and hvm.has_key("mode") and hvm.has_key("disk_target")):
            hvm["driver"] = 'qcow2'
            hvm["mode"] = 'qcow2'
            hvm["disk_target"] = 'vda'
        
        if not (hvm.has_key("target")):
            hvm["target"] = 'vdb'
    
    def create(self,hvm):
        self._set_disk(hvm)
        WindowsVirtualMachine._create(self,hvm)
                
        if hvm.has_key("key"):
            self.vm.add_option("key", hvm["key"])
            
            key_dir = KEY_DIR + "/" + hvm["user"]+"/"+hvm["key"]+"/"
            
            private_key = key_dir + KEY
            public_key = key_dir + KEY+".pub"
            
            self.vm.virtual_machine["context"]["files"] = self.vm.virtual_machine["context"]["files"] + private_key + "    "+ public_key+"    "
        
        if hvm.has_key("files"):
            self.vm.virtual_machine["context"]["files"] = self.vm.virtual_machine["context"]["files"] + hvm["files"] 
        
        if hvm.has_key("flag"):
            self.vm.add_option("flag", hvm["flag"])
            
        
        
        



    
    
    
    

if __name__ == "__main__":   
    
    linux_vm = LinuxVirtualMachine(False)
    hvm = {'count': 1, 'img': '/public/backup/images/base/centos-5.5-x86_64.img', 'vcpu': '2', 'flag': 'paas', 'user': 'test', 'memory': '512'}
    linux_vm.create(hvm)    
    
    print linux_vm.vm.to_content()
    
    windows_vm = WindowsVirtualMachine(True)
    windows_vm.create({"memory":512,"vcpu":1,"user":"wuxl","img":"centos 5","target":"hda","driver":"qcow2","mode":"qcow2","disk_target":"hda"})
    print windows_vm.vm.to_content()
    
    
