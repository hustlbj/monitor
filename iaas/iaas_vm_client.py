from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from crane.thrift import IaaSService

import os, sys
import json

transport = TSocket.TSocket("localhost",10113)
transport.open()
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = IaaSService.Client(protocol)


class IaaSAPI:

    def __init__(self,conf= None,service = None,host="localhost",port = 10113):
	try:
	    self.transport = TSocket.TSocket(host,port)
	    self.transport.open()
	    self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
	    self.client = IaaSService.Client(self.protocol)
	except Exception, e:
		self._fatal(e)

    def _fatal(self,e):
        print >> sys.stderr, "IaaSAPI FATAL ERROR:", e.__str__()
	os._exit(1) 


    def _warn(self,e):
	print >> sys.stderr, "IaaSAPI WARN", e.__str__()
	return [False,"IaaSAPI: " +e.__str__()]

    def get_auth(self, u_name = "crane"):
        try:
            return json.loads(self.client.get_auth(u_name))
        except Exception, e:
            return self._warn(e)
        

    def usercreatekeys( self, username, keyname):
        try:
            return json.loads(self.client.usercreatekeys(username, keyname))
        except Exception, e:
            return self._warn(e)
        

    def userdelkeys( self, username, keyname):
        try:
            return json.loads(self.client.userdelkeys(username, keyname))
        except Exception, e:
            return self._warn(e)
        

    def querykeys( self, username):
        try:
            return json.loads(self.client.querykeys(username))
        except Exception, e:
            return self._warn(e)
        

    def downloadkeys(self, username, keyname):
        try:
            return json.loads(self.client.downloadkeys(username, keyname))
        except Exception, e:
            return self._warn(e)
        

    def get_hostpool_info(self):
        try:
            return json.loads(self.client.get_hostpool_info())
        except Exception, e:
            return self._warn(e)
        
        
    def get_host_info(self, host_id):
        try:
            return json.loads(self.client.get_host_info(host_id))
        except Exception, e:
            return self._warn(e)
        
        
    def host_create(self, host, vmm):
        try:
            return json.loads(self.client.host_create(host, vmm))
        except Exception, e:
            return self._warn(e)
        
        
    def host_delete(self, host_id):
        try:
            return json.loads(self.client.host_delete(host_id))
        except Exception, e:
            return self._warn(e)
        

    def get_user_list(self):
        try:
            return json.loads(self.client.get_user_list())
        except Exception, e:
            return self._warn(e)
        
        
    def user_create(self, user):
        try:
            return json.loads(self.client.user_create(user))
        except Exception, e:
            return self._warn(e)
        
        
    def user_delete(self, user):
        try:
            return json.loads(self.client.user_delete(user))
        except Exception, e:
            return self._warn(e)
        
                
    def init_user(self, user):
        try:
            return json.loads(self.client.init_user(user))
        except Exception, e:
            return self._warn(e)
        

    def get_uid(self, user):
        try:
            return json.loads(self.client.get_uid(user))
        except Exception, e:
            return self._warn(e)
        
    
    def get_imagepool_info(self, user):
        try:
            return json.loads(self.client.get_imagepool_info(user))
        except Exception, e:
            return self._warn(e)
        
    
    def get_image_info(self, user):
        try:
            return json.loads(self.client.get_image_info(user))
        except Exception, e:
            return self._warn(e)
        
            
    def get_all_vmpool_info(self, user):
        try:
            return json.loads(self.client.get_all_vmpool_info(user))
        except Exception, e:
            return self._warn(e)
        
        
    def get_vms_host(self, host_name):
        try:
            return json.loads(self.client.get_vms_host(host_name))
        except Exception, e:
            return self._warn(e)
                    
    
    def get_vmpool_info(self, user, flag = "iaas"):
        try:
            return json.loads(self.client.get_vmpool_info(user, flag))
        except Exception, e:
            return self._warn(e)
       

    def get_vms_info(self, flag = -2, template = 1):
        try:
            return json.loads(self.client.get_vms_info(flag ,template))
        except Exception, e:
            return self._warn(e)
        
    
    def run_remote_command(self, user, vm_id, command):
        try:
            return json.loads(self.client.run_remote_command(user, vm_id, command))
        except Exception, e:
            return self._warn(e)
        
        
    def get_vm_status(self, vm_id):
        try:
            return json.loads(self.client.get_vm_status(vm_id))
        except Exception, e:
            return self._warn(e)
        
        
    def vm_action(self, user, action, vm_id):
        try:
            return json.loads(self.client.vm_action(user, action, vm_id))
        except Exception, e:
            return self._warn(e)
        
        
    def vm_create(self, HVM):
        try:
            HVM = json.dumps(HVM)
            return json.loads(self.client.vm_create(HVM))
        except Exception, e:
            return self._warn(e)
        
        
    def vm_create_details(self,user_name, memory, vcpu, image_dir, count, userkey,start='now', duration='01:00:00', meepo='none'):
        try:
            return json.loads(self.client.vm_create_details(user_name, memory, vcpu, image_dir, count, userkey,start, duration, meepo))
        except Exception, e:
            return self._warn(e)
        

    def vm_delete(self, user, vm_id):
        try:
             return json.loads(self.client.vm_delete(user, vm_id))
        except Exception, e:
            return self._warn(e)
       
        
    def vm_destroy(self, user, vm_id):
        try:
            return json.loads(self.client.vm_destroy(user, vm_id))
        except Exception, e:
            return self._warn(e)
        
        
    def vm_migrate(self, user, vm_id, host_id, livemigration = False):
        try:
            return json.loads(self.client.vm_migrate(user, vm_id, host_id, livemigration))
        except Exception, e:
            return self._warn(e)
        
    def get_vm_info(self, vm_id):
        try:
            return json.loads(self.client.get_vm_info(vm_id))
        except Exception, e:
            return self._warn(e)
        

    def get_vm_lcm_status(self, vm_id):
        try:
            return json.loads(self.client.get_vm_lcm_status(vm_id))
        except Exception, e:
            return self._warn(e)
        

    def vm_sub(self, auth, CON_F):
        try:
            return json.loads(self.client.vm_sub(auth, CON_F))
        except Exception, e:
            return self._warn(e)
        

    def vms_submit(self, user, CON_F, num, os):
        try:
            return json.loads(self.client.vms_submit(user, CON_F, num, os))
        except Exception, e:
            return self._warn(e)
        
        
    def get_vm_ipv6(self, vmid):
        try:
            return json.loads(self.client.get_vm_ipv6(vmid))
        except Exception, e:
            return self._warn(e)
        

    def get_vm_ip(self, id):
        try:
            return json.loads(self.client.get_vm_ip(id))
        except Exception, e:
            return self._warn(e)
        
              
    def get_ip_list(self, user, id_list):
        try:
            id_list = json.dumps(id_list)
            return json.loads(self.client.get_ip_list(user, id_list))
        except Exception, e:
            return self._warn(e)
        

    def get_image_detail(self,user, image_name):
        try:
            return json.loads(self.client.get_image_detail(user, image_name))
        except Exception, e:
            return self._warn(e)

if __name__  == "__main__":
	iaas= IaaSAPI()
	rlt =  iaas.get_user_list()
	print type(rlt)
	print rlt
