#!/usr/bin/env python
"""
Created on Sep 4,2012

@author LiYC
"""

import os
import re
import sys
import time
import hashlib
import xmlrpclib
import subprocess

from BaseIaaS import BaseIaaS
from common import xml2dict
#from common import iaasutil
#from common import userkeys
#import net_attach
from common import remoteExeCommand
from common.exception import RpcDownException, RpcErrorException

from common.vm_content import ONE_RPC_URI, ONE_DATA

from eventtrace.import_utils import import_module
iaasutil = import_module('common.iaasutil')
net_attach = import_module('net_attach')
userkeys = import_module('common.userkeys')

class IaaSOperation(BaseIaaS):
    
    def __init__(self):
        super(BaseIaaS, self).__init__()
        self.rpc_server = xmlrpclib.ServerProxy(ONE_RPC_URI)
        self.xml = xml2dict.XML2Dict()
    
    def get_auth(self, u_name = "crane"):
        '''get the auth of the user
        '''
        return str(u_name)+":"+hashlib.sha1(str(u_name)+"pass").hexdigest()
    
    
    '''
    Interface About User Keys
    '''
    def usercreatekeys( self, username, keyname):
        '''user create keys
        '''
        return userkeys.usercreatekeys(username, keyname)

    def userdelkeys( self, username, keyname):
        '''user delete keys
        '''
        return userkeys.userdelkeys( username, keyname)

    def querykeys( self, username):
        '''query user's keys
        '''
        return userkeys.querykeys( username)    

    def downloadkeys(self, username, keyname):
        '''get the key content
        '''
        return userkeys.downloadkeys(username, keyname)


    '''
    Interface About Host
    '''
    def get_hostpool_info(self):
        '''get hostpool information
        '''
        auth = self.get_auth()


        try:
            result = self.rpc_server.one.hostpool.info(auth)
        except:
            raise RpcDownException(msg= "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            result[1] = []
            if "HOST" in ret.HOST_POOL:
                if type(ret.HOST_POOL.HOST) is list:
                    for each in ret.HOST_POOL.HOST:
                        result[1].append(iaasutil.host_xml_dict(each))
                else:
                        result[1].append(iaasutil.host_xml_dict(ret.HOST_POOL.HOST))
        return result
        
    def get_host_info(self, host_id):
        '''get host information
        '''
        auth = self.get_auth()
        try:
            result = self.rpc_server.one.host.info(auth, int(host_id))
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            result[1] = iaasutil.host_xml_dict(ret.HOST)
        return result
        
    def host_create(self, host, vmm):
        '''add a host to the host resource pool
        '''
        auth = self.get_auth()
        print host+" and "+ vmm
        try:
            result = self.rpc_server.one.host.allocate(auth, host, "im_"+vmm, "vmm_"+vmm, "tm_ssh", True)
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        return result
        
    def host_delete(self, host_id):
        '''delete a host from the host pool
        '''
        auth = self.get_auth()
        try:
            result = self.rpc_server.one.host.delete(auth, int(host_id))
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        return [True, "Delete Host OK!"]
        
    
    
    '''
    Interface About User
    '''
    def get_user_list(self):
        '''get the list of users
        '''
        auth = self.get_auth()
        try:
            result = self.rpc_server.one.userpool.info(auth)
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            result[1] = []
            if "USER" in ret.USER_POOL:
                if type(ret.USER_POOL.USER) is list:
                    for each in ret.USER_POOL.USER:
                        result[1].append(each.NAME)
                else:
                        result[1].append(ret.USER_POOL.USER.NAME)
        return result
        
    def user_create(self, user):
        '''register a user
        '''
        auth = self.get_auth()
        password = hashlib.sha1(str(user) + "pass").hexdigest()
        try:
            result = self.rpc_server.one.user.allocate(auth, str(user), str(password))
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        return result
        
    def user_delete(self, user):
        '''delete a user with user name
        '''
        auth = self.get_auth()
        user_id = self.get_uid(user)
        try:
            result = self.rpc_server.one.user.delete(auth, int(user_id))
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        return [True, "User Delete OK!"]
        
        
    def init_user(self, user):
        '''initialize the user. If the user is not exist, create it.
        '''
        flag, list = self.get_user_list()
        if flag:
            if str(user) not in list:
                return self.user_create(user)
            else:
                return [True, "The user already exists."]
        return [flag, list]
        
    def get_uid(self, user):
        '''get the id of the user
        '''
        auth = self.get_auth()
        result = self.rpc_server.one.userpool.info(auth)
        if result[0]:
            ret = self.xml.fromstring(result[1])
            user_list = ret.USER_POOL.USER
            if type(user_list) is list:
                for each in user_list:
                    if each.NAME == user:
                        return each.ID
            else:
                if user_list.NAME == user:
                    return user_list.ID
        return -1
    
    
    
    '''
    Interface About Image
    '''     
    def get_imagepool_info(self, user):
        '''get the detail information of images
        '''
        auth = self.get_auth(user)
        try:
            result = self.rpc_server.one.imagepool.info(auth,-1)
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            rls = {}
            if "IMAGE" in ret.IMAGE_POOL:
                if type(ret.IMAGE_POOL.IMAGE) is list:
                    for each in ret.IMAGE_POOL.IMAGE:
                        rls[each.NAME]=each.RUNNING_VMS
                else:
                        rls[ret.IMAGE_POOL.IMAGE.NAME]=ret.IMAGE_POOL_IMAGE.RUNNING_VMS
        return [True, rls]
    
    def get_image_info(self, user):
        '''get the list of images available
        '''
        auth = self.get_auth(user)
        try:
            result = self.rpc_server.one.imagepool.info(auth, -1)
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            result[1] = []
            if "IMAGE" in ret.IMAGE_POOL:
                if type(ret.IMAGE_POOL.IMAGE) is list:
                    for each in ret.IMAGE_POOL.IMAGE:
                        result[1].append(each.NAME)
                else:
                        result[1].append(ret.IMAGE_POOL.IMAGE.NAME)
        return result 
    
    '''
    Interface About Vmpool Or VmList
    '''
##    def get_vmpool_info(self,  user):
##        '''get the information of the vms which owned to the user
##          and the LCM_STATE!=12 (shutdown)
##        '''
##        auth = self.get_auth(user)
##        try:
##            result = self.rpc_server.one.vmpool.info(auth, -1)
##        except:
##            raise RpcDownException
##        if not result[0]:
##            raise RpcErrorException(msg= result[1])
##        else:
##            ret = self.xml.fromstring(result[1])
##            result[1] = []
##            if "VM" in ret.VM_POOL:
##                if type(ret.VM_POOL.VM) is list:
##                    for each in ret.VM_POOL.VM:
##                        if each.TEMPLATE.FLAG=='iaas' and int(each.LCM_STATE) !=  12:# and int(each.LCM_STATUS) != 12:
##                            result[1].append(iaasutil.vm_xml_dict(each))
##                else:
##                    if ret.VM_POOL.VM.TEMPLATE.FLAG=='iaas' and int(ret.VM_POOL.VM.LCM_STATE) != 12:
##                        result[1].append(iaasutil.vm_xml_dict(ret.VM_POOL.VM))
##        return result
        
    def get_all_vmpool_info(self, user):
        '''get the information of the vms which owned to the user
        '''
        auth = self.get_auth(user)
        try:
            result = self.rpc_server.one.vmpool.info(auth, -1)
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            result[1] = []
            if "VM" in ret.VM_POOL:
                if type(ret.VM_POOL.VM) is list:
                    for each in ret.VM_POOL.VM:
                        result[1].append(iaasutil.vm_xml_dict(each))
                else:
                    result[1].append(iaasutil.vm_xml_dict(ret.VM_POOL.VM))
        return result
        
    def get_vms_host(self, host_name):
        ''' get the list of vms on a host
        '''
        vms_list = [];
        ret = self.get_vms_info()
        if ret[0]:
            for each in ret[1]:
                if each["hostMachine"] == host_name:
                    vms_list.append(each["guid"])   
        return vms_list
        
##    def get_vms_info(self, flag = -2, template = 1):
##        '''get the information of all the vms
##        '''
##        auth = self.get_auth()
##        try:
##            result = self.rpc_server.one.vmpool.info(auth, flag)
##        except:
##            raise RpcDownException(msg = "IaaS is Down!")
##        else:
##            ret = self.xml.fromstring(result[1])
##            result[1] = []
##            if template==1:
##                if "VM" in ret.VM_POOL:
##                    if type(ret.VM_POOL.VM) is list:
##                            for each in ret.VM_POOL.VM:
##                                if each.TEMPLATE.FLAG=='iaas':
##                                    result[1].append(iaasutil.vm_xml_dict(each))
##                    else:
##                        if ret.VM_POOL.VM.TEMPLATE.FLAG=='iaas':
##                            result[1].append(iaasutil.vm_xml_dict(ret.VM_POOL.VM))
##            if template==0:
##                if "VM" in ret.VM_POOL:
##                    if type(ret.VM_POOL.VM) is list:
##                            for each in ret.VM_POOL.VM:
##                                result[1].append(iaasutil.vm_xml_dict(each))
##                    else:
##                        result[1].append(iaasutil.vm_xml_dict(ret.VM_POOL.VM))
##        return result
        
    
    def get_vmpool_info(self, user, flag = "iaas"):
        '''get the information of the vms which owned to the user
        '''
        auth = self.get_auth(user)

        try:
            result = self.rpc_server.one.vmpool.info(auth, -1)
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            result[1] = []
            if "VM" in ret.VM_POOL:
                if type(ret.VM_POOL.VM) is list:
                    for each in ret.VM_POOL.VM:
                        if each.TEMPLATE.FLAG== flag and int(each.LCM_STATE) !=  12 \
                           and int(each.LCM_STATE) != 16:
                            result[1].append(iaasutil.vm_xml_dict(each))
                else:
                    if ret.VM_POOL.VM.TEMPLATE.FLAG== flag and int(ret.VM_POOL.VM.LCM_STATE) != 12 \
                       and int(ret.VM_POOL.VM.LCM_STATE) != 16:
                        result[1].append(iaasutil.vm_xml_dict(ret.VM_POOL.VM))
        return result
        
    def get_vms_info(self, flag = -2, template = 1):
        '''get the information of all the vms
        '''
        auth = self.get_auth()
        try:
            result = self.rpc_server.one.vmpool.info(auth, flag)
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            result[1] = []
            if template==1:
                if "VM" in ret.VM_POOL:
                    if type(ret.VM_POOL.VM) is list:
                        for each in ret.VM_POOL.VM:
                            if each.TEMPLATE.FLAG=='iaas':
                                result[1].append(iaasutil.vm_xml_dict(each))
                    else:
                        if ret.VM_POOL.VM.TEMPLATE.FLAG=='iaas':
                            result[1].append(iaasutil.vm_xml_dict(ret.VM_POOL.VM))
            if template==0:
                if "VM" in ret.VM_POOL:
                        if type(ret.VM_POOL.VM) is list:
                            for each in ret.VM_POOL.VM:
                                result[1].append(iaasutil.vm_xml_dict(each))
                        else:
                            result[1].append(iaasutil.vm_xml_dict(ret.VM_POOL.VM))
        return result
    
    '''
    Special Interface such as run_remote_command
    '''
    def run_remote_command(self, user, vm_id, command):
        '''Run remote command on the vm,and get the return data
        '''
        remote_ip = ""
        try:
            vm_list = self.get_all_vmpool_info(user)
        except (RpcDownException,RpcErrorException) as err:
            return [False, str(err)]
        for vm_info in vm_list[1]:
            if vm_info['guid'] == str(vm_id):
                remote_ip = vm_info['ip']
                break;
        if remote_ip == "":
            return [False, "Get ip error! Make sure this is your virtual machine!"]
        try:
            vmxmlrpc_server = xmlrpclib.ServerProxy("http://"+remote_ip+":6534")
            ret = vmxmlrpc_server.run_command( command)
            print ret
            if not ret[0]:
                return [True, ret[1]]
            return [False, ret[1]]
        except Exception,e:
            return [False, str(e)]
    

    '''
    Interface About VM
    '''
##    def get_vm_info(self, vm_id):
##        '''get the information of the vm
##        '''
##        auth = self.get_auth()
##        try:
##            result = self.rpc_server.one.vm.info(auth, int(vm_id))
##        except:
##            raise RpcDownException(msg ="IaaS is Down!")
##        if not result[0]:
##            raise RpcErrorException(msg = result[1])
##        else:
##            ret = self.xml.fromstring(result[1])
##            result[1] = {}
##            result[1]["id"] = vm_id
##            result[1]["ip"] = ret.VM.TEMPLATE.NIC[0].IP
##            result[1]["port"] = iaasutil.get_ssh_port(str(vm_id)) 
##            #result[1]["port"] = int(ret.VM.TEMPLATE.GRAPHICS.PORT) + 5900
##            result[1]["host"] = ret.VM.HISTORY.HOSTNAME
##            result[1]["vcpu"] = ret.VM.TEMPLATE.VCPU
##            result[1]["stime"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(ret.VM.STIME)))
##        return result
        
    def get_vm_status(self, vm_id):
        '''get the information of the vm
        '''
        auth = self.get_auth()
        state = ["INIT", "PENDING", "HOLD", "RUNNING", "STOPPED", "SUSPENDED", "DONE", "FAIL"]
        try:
            result = self.rpc_server.one.vm.info(auth, int(vm_id))
        except:
            raise RpcDownException(msg ="IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            result[1] = state[int(ret.VM.STATE)]
        return result
        
    def vm_action(self, user, action, vm_id):
        '''control the vm. action can be shutdown,suspend,resume
        '''
        auth = self.get_auth(user)
        ip = self.get_vm_ip(str(vm_id))
        print "ip",ip
        try:
            result = self.rpc_server.one.vm.action(auth, action, int(vm_id))
        #    ret = remoteExeCommand.shutdown(ip)
        #    print ret
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException( msg = result[1])
        if action == 'shutdown':
            net_attach.release_ssh_port(str(vm_id))
        return [True, "Vm Action OK!"]
        
    def vm_create(self, HVM):
        '''creat vms with a configure file
        '''
        iaasutil.init_conf(HVM)        
        image_detail = self.get_image_detail(HVM['user'],HVM['img'])
        if HVM['flag'] == 'iaas':
            if image_detail == None:
                raise Exception("can not confirm os type of the image ","vm_create")
            HVM['os'] = image_detail[0]
            HVM['arch'] = image_detail[1]
        else:
            HVM['os'] = 'LINUX'
        CONF_FILE= iaasutil.create_vm_template(HVM)
        print CONF_FILE
        try:
            with open(CONF_FILE, "r") as fp:
                fp_content = fp.read().strip()
        except EnvironmentError:
            return [False, "File Open Error:%s" % CONF_FILE]
        id_list = self.vms_submit(str(HVM["user"]), fp_content, int(HVM["count"]), HVM["os"])
        if id_list[0]:
            result = self.get_ip_list(str(HVM["user"]), id_list[1])           
            return result
        else:
            return id_list
        
    def vm_create_details(self,user_name, memory, vcpu, image_dir, count, userkey,start='now', duration='01:00:00', meepo='none'):
        '''creat vms with a some parameters
        '''
        hvm_file = { 'user': user_name, 'memory': memory, 'vcpu': vcpu, 'img': image_dir, 'count': count, 'start': start, 'duration': duration,'key':userkey, 'meepo': meepo}
        return self.vm_create(hvm_file)

    def vm_delete(self, user, vm_id):
        '''delete a vm of the user with the id
        '''
        auth = self.get_auth(user)
        try:
            result = self.rpc_server.one.vm.action(auth, "finalize", int(vm_id))
        except:
            raise RpcDownException( msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException( msg = result[1])
        net_attach.release_ssh_port(str(vm_id))
        return [True, "Vm Delete OK!"]
        
    def vm_destroy(self, user, vm_id):
        '''destroy a vm of the user with the id
        '''
        shutdown_rls = self.vm_action(user, "shutdown", vm_id)
        delete_rls = self.vm_delete(user, vm_id);
        
        if shutdown_rls[0] == True and delete_rls[0] == True:
            return [True, "Vm Destroy OK!"]
        return [False, shutdown_rls[1]+delete_rls[1]]
        
    def vm_migrate(self, user, vm_id, host_id, livemigration = False):
        '''migrate a vm with id to the host with host_id
        '''
        auth = self.set_auth(user)
        try:
            result = self.rpc_server.one.vm.migrate(auth, int(vm_id), int(host_id), livemigration)
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        return [True, "Vm Migrate OK!"]
        
    
    def get_vm_info(self, vm_id):
        '''get the information of the vm
        '''
        auth = self.get_auth()
        try:
            result = self.rpc_server.one.vm.info(auth, int(vm_id))
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            result[1] = {}
            result[1]["id"] = vm_id
            if type(ret.VM.TEMPLATE.NIC) is list:
                result[1]["ip"] = ret.VM.TEMPLATE.NIC[0].IP
            else:
                result[1]["ip"] = ret.VM.TEMPLATE.NIC.IP
            result[1]["vcpu"] = ret.VM.TEMPLATE.VCPU
            result[1]["memory"] = ret.VM.TEMPLATE.MEMORY
            if "IMAGE" in ret.VM.TEMPLATE.DISK:
                result[1]["image"] = ret.VM.TEMPLATE.DISK.IMAGE
            else:
                result[1]["image"] = ""
        
            if "KEY" in ret.VM.TEMPLATE:
                result[1]["key"] = ret.VM.TEMPLATE.KEY
            else:
                result[1]["key"]=""
            result[1]["ipv6"] = self.get_vm_ipv6(str(vm_id))
        
            rl =  net_attach.query_ssh_port(str(vm_id))
            if rl[0] == True:
                result[1]["sshport"] = rl[1]
            else:
                result[1]["sshport"] =  ""
            rl = net_attach.query_dns(str(vm_id))
            if rl[0]  == True:
                result[1]["dns"] = rl[1]
            else:
                result[1]["dns"] = ""
        
        return result
        
    def get_vm_lcm_status(self, vm_id):
        '''get the lcm status 
        '''
        lcm_state = ["LCM_INIT","PROLOG","BOOT","RUNNING","MIGRATE","SAVE_STOP","SAVE_SUSPEND","SAVE_MIGRATE","PROLOG_MIGRATE","PROLOG_RESUME",\
                "EPILOG_STOP","EPILOG","SHUTDOWN","CANCEL","FAILURE","CLEANUP","UNKNOWN"]
        auth = self.get_auth()
        try:
            result = self.rpc_server.one.vm.info(auth,int(vm_id))
        except:
            raise RpcDownException(msg ="IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            result[1] = lcm_state[int(ret.VM.LCM_STATE)]
        return result
        
    def vm_sub(self, auth, CON_F):
        '''create a vm
        '''
        try:
            result = self.rpc_server.one.vm.allocate(auth, CON_F)
        except:
            return -1
        if result[0]:
            return result[1]
        else:
            return -1
    
    def vms_submit(self, user, CON_F, num, os):
        '''create vms one by one
        '''
        auth = self.get_auth(user)
        ids = []
        index = 0
        while index < num:
            try:
                result = self.rpc_server.one.vm.allocate(auth, CON_F)
            except:
                raise RpcDownException(msg = "IaaS is Down!")
            if result[0]:
                index += 1
                ids.append(result[1])                   
                ip = self.get_vm_ip(result[1])
                if os == 'WINDOWS':
                    rl = net_attach.get_port(str(result[1]),ip,"5900") # for vnc port
                else:
                    rl = net_attach.get_port(str(result[1]),ip, "22") # for ssh port
                rl = net_attach.set_dns(str(result[1])) 
            else:
                for each in ids:
                    self.vm_delete(user, each) 
                return result
        return [True, ids]
        
    def get_vm_ipv6(self, vmid):
        '''get the ipv6 address of the vm
        '''
        rls = net_attach.query_ipv6( str(vmid) )
        if rls[0] == True:
            return rls[1]
        return ""

    def get_vm_ip(self, id):
        '''get the ip of the vm with id
        '''
        auth = self.get_auth()
        try:
            result = self.rpc_server.one.vm.info(auth, int(id))
        except:
            return "-1"
        if result[0]:
            is_ip = re.search('<IP><!\[CDATA\[([\.0-9]*)\]\]></IP>', result[1])
            if is_ip:
                return is_ip.group(1)
            else:
                return "-1" 
        else:
            return "-1"
        
    def get_ip_list(self, user, id_list):
        '''get ips from ids one by one
        '''
        auth = self.get_auth(user)
        ip_list = []
        for each in id_list:
            flag = False
            while not flag:
                try:
                    result = self.rpc_server.one.vm.info(auth, int(each))
                    flag = result[0]
                except:
                    raise RpcDownException(msg ="IaaS is Down!")
            if result[0]:
                is_ip = re.search('<IP><!\[CDATA\[([\.0-9]*)\]\]></IP>', result[1])
                if is_ip:
                    ip_list.append([str(each), is_ip.group(1) ])
                    #ip_list.append([str(each), is_ip.group(1) , '''fec0:0:0:1::''' + is_ip.group(1)])
        return [True,ip_list]

    def get_image_detail(self,user, image_name):
        print user , image_name
        auth = self.get_auth(user)
        try:
            result = self.rpc_server.one.imagepool.info(auth, -1)
            print result
        except:
            raise RpcDownException(msg = "IaaS is Down!")
        if not result[0]:
            raise RpcErrorException(msg = result[1])
        else:
            ret = self.xml.fromstring(result[1])
            if "IMAGE" in ret.IMAGE_POOL:
                if type(ret.IMAGE_POOL.IMAGE) is list:
                    for each in ret.IMAGE_POOL.IMAGE:
                        if each.NAME == image_name:
                            if "OS" in each.TEMPLATE and "ARCH" in each.TEMPLATE:
                                return [each.TEMPLATE.OS, each.TEMPLATE.ARCH]
                else:
                    if "OS" in each.TEMPLATE and "ARCH" in each.TEMPLATE:
                        return [each.TEMPLATE.OS, each.TEMPLATE.ARCH]
        return None


if __name__ == '__main__':
    #hvm = {'count': 1, 'img': 'windows-server', 'vcpu': '2', 'flag': 'iaas', 'user': 'test', 'memory': '1024'}
    hvm = {'count': 1, 'img': 'centos-5.5-x86_64', 'key':'default','vcpu': '2', 'flag': 'iaas', 'user': 'test', 'memory': '1024'}
    #hvm={'vcpu': '1', 'count': 1, 'user': 'test', 'img': 'windows-server','memory': '256','flag':'iaas','key':'default'}
    iaas = IaaSOperation()
    print iaas.get_all_vmpool_info('test')
    #print iaas.vm_create(hvm)
    #print iaas.vm_delete('test',99)
    #print iaas.vm_delete('test',102)
    #print iaas.get_vm_info('9')
