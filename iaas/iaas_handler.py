#!/usr/bin/env python
"""
Created on Sep 4,2012

@author LiYC
"""
import os, sys
import json
#from IaaSOperation import IaaSOperation as IaaS
from eventtrace.import_utils import import_class
IaaS = import_class('IaaSOperation.IaaSOperation')

class IaaSHandler(object):
    
    def __init__(self):
        self.iaas = IaaS()

    def _warn(self, e):
        print >> sys.stderr, "IaaSHandler: WARN: ", e.__str__()
        return json.dumps(None)
    
    def get_auth(self, u_name = "crane"):
	print >> sys.stderr, "get_auth"
        try:
            return json.dumps(self.iaas.get_auth(u_name))
        except Exception, e:
            return self._warn(e)
        

    def usercreatekeys( self, username, keyname):
        try:
            return json.dumps(self.iaas.usercreatekeys(username, keyname))
        except Exception, e:
            return self._warn(e)
        

    def userdelkeys( self, username, keyname):
        try:
            return json.dumps(self.iaas.userdelkeys(username, keyname))
        except Exception, e:
            return self._warn(e)
        

    def querykeys( self, username):
        try:
            return json.dumps(self.iaas.querykeys(username))
        except Exception, e:
            return self._warn(e)
        

    def downloadkeys(self, username, keyname):
        try:
            return json.dumps(self.iaas.downloadkeys(username, keyname))
        except Exception, e:
            return self._warn(e)
        

    def get_hostpool_info(self):
        try:
            return json.dumps(self.iaas.get_hostpool_info())
        except Exception, e:
            return self._warn(e)
        
        
    def get_host_info(self, host_id):
        try:
            return json.dumps(self.iaas.get_host_info(host_id))
        except Exception, e:
            return self._warn(e)
        
        
    def host_create(self, host, vmm):
        try:
            return json.dumps(self.iaas.host_create(host, vmm))
        except Exception, e:
            return self._warn(e)
        
        
    def host_delete(self, host_id):
        try:
            return json.dumps(self.iaas.host_delete(host_id))
        except Exception, e:
            return self._warn(e)
        

    def get_user_list(self):
        try:
            return json.dumps(self.iaas.get_user_list())
        except Exception, e:
            return self._warn(e)
        
        
    def user_create(self, user):
        try:
            return json.dumps(self.iaas.user_create(user))
        except Exception, e:
            return self._warn(e)
        
        
    def user_delete(self, user):
        try:
            return json.dumps(self.iaas.user_delete(user))
        except Exception, e:
            return self._warn(e)
        
                
    def init_user(self, user):
        try:
            return json.dumps(self.iaas.init_user(user))
        except Exception, e:
            return self._warn(e)
        

    def get_uid(self, user):
        try:
            return json.dumps(self.iaas.get_uid(user))
        except Exception, e:
            return self._warn(e)
        
    
    def get_imagepool_info(self, user):
        try:
            return json.dumps(self.iaas.get_imagepool_info(user))
        except Exception, e:
            return self._warn(e)
        
    
    def get_image_info(self, user):
        try:
            return json.dumps(self.iaas.get_image_info(user))
        except Exception, e:
            return self._warn(e)
        
            
    def get_all_vmpool_info(self, user):
        try:
            return json.dumps(self.iaas.get_all_vmpool_info(user))
        except Exception, e:
            return self._warn(e)
        
        
    def get_vms_host(self, host_name):
        try:
            return json.dumps(self.iaas.get_vms_host(host_name))
        except Exception, e:
            return self._warn(e)
                    
    
    def get_vmpool_info(self, user, flag = "iaas"):
	print >> sys.stderr, "get_vmpool_info"
        try:
            return json.dumps(self.iaas.get_vmpool_info(user, flag))
        except Exception, e:
            return self._warn(e)
       

    def get_vms_info(self, flag = -2, template = 1):
	print >> sys.stderr, "get_vms_info"
        try:
            return json.dumps(self.iaas.get_vms_info(flag ,template))
        except Exception, e:
            return self._warn(e)
        
    
    def run_remote_command(self, user, vm_id, command):
        try:
            return json.dumps(self.iaas.run_remote_command(user, vm_id, command))
        except Exception, e:
            return self._warn(e)
        
        
    def get_vm_status(self, vm_id):
        try:
            return json.dumps(self.iaas.get_vm_status(vm_id))
        except Exception, e:
            return self._warn(e)
        
        
    def vm_action(self, user, action, vm_id):
        try:
            return json.dumps(self.iaas.vm_action(user, action, vm_id))
        except Exception, e:
            return self._warn(e)
        
        
    def vm_create(self, HVM):
        try:
            HVM = json.loads(HVM)
            return json.dumps(self.iaas.vm_create(HVM))
        except Exception, e:
            return self._warn(e)
        
        
    def vm_create_details(self,user_name, memory, vcpu, image_dir, count, userkey,start='now', duration='01:00:00', meepo='none'):
        try:
            return json.dumps(self.iaas.vm_create_details(user_name, memory, vcpu, image_dir, count, userkey,start, duration, meepo))
        except Exception, e:
            return self._warn(e)
        

    def vm_delete(self, user, vm_id):
        try:
             return json.dumps(self.iaas.vm_delete(user, vm_id))
        except Exception, e:
            return self._warn(e)
       
        
    def vm_destroy(self, user, vm_id):
        try:
            return json.dumps(self.iaas.vm_destroy(user, vm_id))
        except Exception, e:
            return self._warn(e)
        
        
    def vm_migrate(self, user, vm_id, host_id, livemigration = False):
        try:
            return json.dumps(self.iaas.vm_migrate(user, vm_id, host_id, livemigration))
        except Exception, e:
            return self._warn(e)
        
    def get_vm_info(self, vm_id):
        try:
            return json.dumps(self.iaas.get_vm_info(vm_id))
        except Exception, e:
            return self._warn(e)
        

    def get_vm_lcm_status(self, vm_id):
        try:
            return json.dumps(self.iaas.get_vm_lcm_status(vm_id))
        except Exception, e:
            return self._warn(e)
        

    def vm_sub(self, auth, CON_F):
        try:
            return json.dumps(self.iaas.vm_sub(auth, CON_F))
        except Exception, e:
            return self._warn(e)
        

    def vms_submit(self, user, CON_F, num, os):
        try:
            return json.dumps(self.iaas.vms_submit(user, CON_F, num, os))
        except Exception, e:
            return self._warn(e)
        
        
    def get_vm_ipv6(self, vmid):
        try:
            return json.dumps(self.iaas.get_vm_ipv6(vmid))
        except Exception, e:
            return self._warn(e)
        

    def get_vm_ip(self, id):
        try:
            return json.dumps(self.iaas.get_vm_ip(id))
        except Exception, e:
            return self._warn(e)
        
              
    def get_ip_list(self, user, id_list):
        try:
            id_list = json.loads(id_list)
            return json.dumps(self.iaas.get_ip_list(user, id_list))
        except Exception, e:
            return self._warn(e)
        

    def get_image_detail(self,user, image_name):
        try:
            return json.dumps(self.iaas.get_image_detail(user, image_name))
        except Exception, e:
            return self._warn(e)
        




