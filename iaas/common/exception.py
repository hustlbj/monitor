#!/usr/bin/env python
"""
Created on Sep 4,2012

@author LiYC
"""

class CommonException(Exception):
    """
    Base Exception
    """
    message = "An exception occured"
    
    def __init__(self,**kwargs):
        try:
            self._error_str = self.message % kwargs
        except Exception:
            self._error_str = self.message
            
            
    def __str__(self):
        return self._error_str

   
class RpcDownException(CommonException):
    """
    Rpc Method Can't Work
    """
    message = "Rpc Down Fail: %(msg)s"

class RpcErrorException(CommonException):
    """
    False Return of Rpc invoke
    """
    message = "Rpc Invoke Fail: %(msg)s"
