from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from cloud.iaas.crane.thrift import IaaSService

import os, sys
import json


class IaaSAPI(object):

    def __init__(self,conf= None,service = None,host="localhost",port = 10113):
	try:
	    self.socket = TSocket.TSocket(host,port)
	    self.transport = TTransport.TFramedTransport(self.socket)
	    self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
	    self.client = IaaSService.Client(self.protocol)
	    self.transport.open()
	except Exception, e:
		self._fatal(e)

    def _fatal(self,e):
        print >> sys.stderr, "IaaSAPI FATAL ERROR:", e.__str__()
	os._exit(1) 


    def _warn(self,e):
	print >> sys.stderr, "IaaSAPI WARN", e.__str__()
	return json.dumps([False,"IaaSAPI: " +e.__str__()])

    def get_auth(self, u_name = "crane"):
        try:
            return self.client.get_auth(u_name)
        except Exception, e:
            return self._warn(e)
        

    def usercreatekeys( self, username, keyname):
        try:
            return self.client.usercreatekeys(username, keyname)
        except Exception, e:
            return self._warn(e)
        

    def userdelkeys( self, username, keyname):
        try:
            return self.client.userdelkeys(username, keyname)
        except Exception, e:
            return self._warn(e)
        

    def querykeys( self, username):
        try:
            return self.client.querykeys(username)
        except Exception, e:
            return self._warn(e)
        

    def downloadkeys(self, username, keyname):
        try:
            return self.client.downloadkeys(username, keyname)
        except Exception, e:
            return self._warn(e)
        

    def get_hostpool_info(self):
        try:
            return self.client.get_hostpool_info()
        except Exception, e:
            return self._warn(e)
        
        
    def get_host_info(self, host_id):
        try:
            return self.client.get_host_info(int(host_id))
        except Exception, e:
            return self._warn(e)
        
        
    def host_create(self, host, vmm):
        try:
            return self.client.host_create(host, vmm)
        except Exception, e:
            return self._warn(e)
        
        
    def host_delete(self, host_id):
        try:
            return self.client.host_delete(int(host_id))
        except Exception, e:
            return self._warn(e)
        

    def get_user_list(self):
        try:
            #return self.client.get_user_list()
            return self.client.get_user_list()
        except Exception, e:
            return self._warn(e)
        
        
    def user_create(self, user):
        try:
            return self.client.user_create(user)
        except Exception, e:
            return self._warn(e)
        
        
    def user_delete(self, user):
        try:
            return self.client.user_delete(user)
        except Exception, e:
            return self._warn(e)
        
                
    def init_user(self, user):
        try:
            return self.client.init_user(user)
        except Exception, e:
            return self._warn(e)
        

    def get_uid(self, user):
        try:
            return self.client.get_uid(user)
        except Exception, e:
            return self._warn(e)
        
    
    def get_imagepool_info(self, user):
        try:
            return self.client.get_imagepool_info(user)
        except Exception, e:
            return self._warn(e)
        
    
    def get_image_info(self, user):
        try:
            return self.client.get_image_info(user)
        except Exception, e:
            return self._warn(e)
        
            
    def get_all_vmpool_info(self, user):
        try:
            return self.client.get_all_vmpool_info(user)
            #return self.client.get_all_vmpool_info(user)
        except Exception, e:
            return self._warn(e)
        
        
    def get_vms_host(self, host_name):
        try:
            return self.client.get_vms_host(host_name)
        except Exception, e:
            return self._warn(e)
                    
    
    def get_vmpool_info(self, user, flag = "iaas"):
        try:
            return self.client.get_vmpool_info(user, flag)
            #return self.client.get_vmpool_info(user, flag)
        except Exception, e:
            return self._warn(e)
       

    def get_vms_info(self, flag = -2, template = 1):
        try:
            #return self.client.get_vms_info(flag ,template)
            return self.client.get_vms_info(int(flag) ,int(template))
        except Exception, e:
            return self._warn(e)
        
    
    def run_remote_command(self, user, vm_id, command):
        try:
            return self.client.run_remote_command(user, int(vm_id), command)
        except Exception, e:
            return self._warn(e)
        
        
    def get_vm_status(self, vm_id):
        try:
            return self.client.get_vm_status(int(vm_id))
        except Exception, e:
            return self._warn(e)
        
        
    def vm_action(self, user, action, vm_id):
        try:
            return self.client.vm_action(user, action, int(vm_id))
        except Exception, e:
            return self._warn(e)
        
        
    def vm_create(self, HVM):
        try:
            HVM = json.dumps(HVM)
            return self.client.vm_create(HVM)
        except Exception, e:
            return self._warn(e)
        
        
    def vm_create_details(self,user_name, memory, vcpu, image_dir, count, userkey,start='now', duration='01:00:00', meepo='none'):
        try:
            return self.client.vm_create_details(user_name, int(memory), int(vcpu), image_dir, int(count), userkey,start, duration, meepo)
        except Exception, e:
            return self._warn(e)
        

    def vm_delete(self, user, vm_id):
        try:
             return self.client.vm_delete(user, int(vm_id))
        except Exception, e:
            return self._warn(e)
       
        
    def vm_destroy(self, user, vm_id):
        try:
            return self.client.vm_destroy(user, int(vm_id))
        except Exception, e:
            return self._warn(e)
        
        
    def vm_migrate(self, user, vm_id, host_id, livemigration = False):
        try:
            return self.client.vm_migrate(user, int(vm_id), int(host_id), livemigration)
        except Exception, e:
            return self._warn(e)
        
    def get_vm_info(self, vm_id):
        try:
            return self.client.get_vm_info(int(vm_id))
        except Exception, e:
            return self._warn(e)
        

    def get_vm_lcm_status(self, vm_id):
        try:
            return self.client.get_vm_lcm_status(int(vm_id))
        except Exception, e:
            return self._warn(e)
        

    def vm_sub(self, auth, CON_F):
        try:
            return self.client.vm_sub(auth, CON_F)
        except Exception, e:
            return self._warn(e)
        

    def vms_submit(self, user, CON_F, num, os):
        try:
            return self.client.vms_submit(user, CON_F, int(num), os)
        except Exception, e:
            return self._warn(e)
        
        
    def get_vm_ipv6(self, vmid):
        try:
            return self.client.get_vm_ipv6(int(vmid))
        except Exception, e:
            return self._warn(e)
        

    def get_vm_ip(self, id):
        try:
            return self.client.get_vm_ip(int(id))
        except Exception, e:
            return self._warn(e)
        
              
    def get_ip_list(self, user, id_list):
        try:
            id_list = json.dumps(id_list)
            return self.client.get_ip_list(user, id_list)
        except Exception, e:
            return self._warn(e)
        

    def get_image_detail(self,user, image_name):
        try:
            return self.client.get_image_detail(user, image_name)
        except Exception, e:
            return self._warn(e)

if __name__  == "__main__":
	iaas= IaaSAPI()
	#rlt =  iaas.get_user_list()
	#print type(rlt)
	#print rlt
	#rlt =  iaas.get_image_detail('test001','test001_test')
	#print type(rlt)
	#print rlt
	#rlt =  iaas.get_ip_list('test',[3958,3959])
	#print type(rlt)
	#print rlt
	#rlt =  iaas.get_vm_ip('3958')
	#print type(rlt)
	#print rlt
	#rlt =  iaas.get_vm_lcm_status(3958)
	#print type(rlt)
	#print rlt
	#print iaas.get_vm_info(3958)
	#print iaas.get_vm_status(3958)
	#print iaas.get_vms_info()
	#print iaas.get_vmpool_info('test001')
	#print iaas.vm_action('exper_04','shutdown',4094)
	#print iaas.vm_action('exper_04','shutdown',4095)
	#print iaas.vm_action('exper_04','shutdown',4096)
	#print iaas.vm_action('exper_04','shutdown',4097)
	#print iaas.vm_action('exper_04','shutdown',4098)
#	print iaas.vm_action('exper_04','delete',4099)
	#print iaas.vm_action('hust_test','shutdown',4035)
	#print iaas.vm_action('hust_test','shutdown',4036)
	#print iaas.vm_action('exper_10','shutdown',3942)
	#print iaas.vm_action('exper_01','shutdown',3954)
	#print iaas.vm_action('exper_01','shutdown',3955)
	#print iaas.get_vms_host('node76')
	#print iaas.get_all_vmpool_info('test')
	#print iaas.get_image_info('test001')
	#print iaas.get_imagepool_info('test001')
	#print iaas.get_uid('test')
	#print iaas.user_create('test_hello')
	#print iaas.get_user_list()
	#print iaas.user_delete('test_hello')
	#rlt =  iaas.get_user_list()
	#print type(rlt)
	#print rlt
	#print iaas.get_host_info(1)
	#print iaas.get_hostpool_info()
	#print iaas.usercreatekeys('test','test_wuxl_key')
	print iaas.userdelkeys('test','test_wuxl_key')
	print iaas.querykeys('test')
	#print iaas.downloadkeys('test','test_wuxl_key')
#	print iaas.userdelkeys('test','test_wuxl_key')
#	print iaas.querykeys('test')
