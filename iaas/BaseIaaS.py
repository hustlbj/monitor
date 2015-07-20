#!/usr/bin/env python
"""
Created on Sep 4,2012

@author LiYC
"""
from abc import ABCMeta, abstractmethod


class BaseIaaS:
    __metaclass__ = ABCMeta
    
    def __init__(self):
        pass

    '''
    Interface About Host
    '''
    @abstractmethod
    def get_hostpool_info(self):
        raise NotImplementedError()
    
    @abstractmethod
    def get_host_info(self, host_id):
        raise NotImplementedError()
        
    @abstractmethod
    def host_create(self, host, vmm):
        raise NotImplementedError()
        
    @abstractmethod
    def host_delete(self, host_id):
        raise NotImplementedError()
    
    '''
    Interface About User
    '''    
    @abstractmethod
    def get_user_list(self):
        raise NotImplementedError()
        
    @abstractmethod
    def user_create(self, user):
        raise NotImplementedError()
        
    @abstractmethod
    def user_delete(self, user):
        raise NotImplementedError()
    
    '''
    Interface About Image
    '''      
    @abstractmethod
    def get_imagepool_info(self, user):
        raise NotImplementedError()
        
    @abstractmethod
    def get_image_info(self, user):
        raise NotImplementedError()
        
    '''
    Interface About Vmpool Or VmList
    '''        
    @abstractmethod
    def get_vmpool_info(self,  user):
        raise NotImplementedError()
        
    @abstractmethod
    def get_all_vmpool_info(self, user):
        raise NotImplementedError()
        
    @abstractmethod
    def get_vms_host(self, host_name):
        raise NotImplementedError()
        
    @abstractmethod
    def get_vms_info(self, flag = -2, template = 1):
        raise NotImplementedError()
        
    '''
    Interface About VM
    '''
    @abstractmethod
    def get_vm_info(self, vm_id):
        raise NotImplementedError()
        
    @abstractmethod
    def get_vm_status(self, vm_id):
        raise NotImplementedError()
        
    @abstractmethod
    def vm_action(self, user, action, vm_id):
        raise NotImplementedError()
        
    @abstractmethod
    def vm_create(self, HVM):
        raise NotImplementedError()
        
    @abstractmethod
    def vm_delete(self, user, vm_id):
        raise NotImplementedError()
        
    @abstractmethod
    def vm_migrate(self, user, vm_id, host_id, livemigration = False):
        raise NotImplementedError()

