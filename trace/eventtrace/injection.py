#!/usr/bin/env python

import inspect
import time
import uuid
import socket
import types
import os

curdir = os.path.dirname(os.path.abspath(__file__))
#SOCKFILE = curdir + os.sep + "collector_socket"
SOCKFILE = "/usr/crane/package/trace/eventtrace/collector_socket"

def t_trace(is_method=False):
    def new_decorator(func):
        def post(*args, **kargs):
            cur_comp = func.__module__ + '-'
            if is_method:
                obj = args[0]
                cur_comp += obj.__class__.__name__ + '.'
            cur_comp += func.__name__
     
            if kargs.has_key('trace_id'):
                trace_id = kargs.pop('trace_id')
                last_comp = kargs.pop('last_comp')
            else:
                trace_id = -1
                last_comp = "none"
                for stack_entry in inspect.stack()[1::]:
                    if stack_entry[3] == 'post':
                        frame = stack_entry[0]
                        trace_id = frame.f_locals.get('trace_id', -1)
                        last_comp = frame.f_locals.get('cur_comp', 'none')
                        break
      
            if trace_id == -1:
		print 'trace_id = -1, asign an uuid'
                #return func(*args, **kargs)
		trace_id = str(uuid.uuid1())
		last_comp = None
 
            
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

            ts_start = time.time()
            entry = {'trace': trace_id,
                     'last': last_comp,
                     'current': cur_comp,
                     'start': ts_start,
                     'params': {}}
            try:
                print 't_trace begin:', entry
                sock.sendto(str(entry), SOCKFILE)
            except socket.error, e:
                print str(e)
                pass

            try:
                ret = func(*args, **kargs)
            except Exception, e:
                entry['state'] = False
                entry['end'] = time.time()

                try:
                    print 't_trace exception:', entry
                    sock.sendto(str(entry), SOCKFILE)
                except socket.error, e:
                    pass

                raise e

            #ts_end = time.time()

            entry['end'] = time.time()
            try:
                print 't_trace end:', entry
                sock.sendto(str(entry), SOCKFILE)
            except socket.error, e:
                print str(e)
                pass
            sock.close()

            return ret
        
        return post

    return new_decorator


		
def t_interface(is_method=False):
    def new_decorator(func):		
        def post(*args, **kargs):
           
            # Get name of current component(function)
            cur_comp = func.__module__ + '-'
            if is_method:
                obj = args[0]
                cur_comp += obj.__class__.__name__ + '.'
            cur_comp += func.__name__
   
            frame = None
            for stack_entry in inspect.stack()[1::]:
                if stack_entry[3] == 'post':
                    frame = stack_entry[0]
                    break
    
            if frame:
                trace_id = frame.f_locals.get('trace_id', -1)
                last_comp = frame.f_locals.get('cur_comp', 'none')
            else:
                trace_id = str(uuid.uuid4())
                last_comp = 'none'
   
            if trace_id == -1:
                return func(*args, **kargs)

 
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

            ts_start = time.time()
            entry = {'trace': trace_id,
                     'last': last_comp,
                     'current': cur_comp,
                     'start': ts_start,
                     'params':[list(args)[1::], kargs]}
            try:
                print 't_interface begin:', entry
                sock.sendto(str(entry), SOCKFILE)
            except socket.error, e:
                pass

            try:
                ret = func(*args, **kargs)
            except Exception, e:
                entry['state'] = False
                entry['end'] = time.time()

                try:
                    print 't_interface exception:', entry
                    sock.sendto(str(entry), SOCKFILE)
                except socket.error, e:
                    pass

                raise e

            #ts_end = time.time()

            entry['end'] = time.time()
            try:
                print 't_interface end:', entry
                sock.sendto(str(entry), SOCKFILE)
            except socket.error, e:
                pass
            sock.close()
   
            return ret
    
        return post

    return new_decorator


class TraceMeta(type):
    def __new__(cls, name, bases, dct):
        for key, value in bases[0].__dict__.items():
            if not key.startswith('__') and inspect.isfunction(value):
                value = t_trace(True)(value)
                dct[key] = value

        return type.__new__(cls, name, bases, dct)


class InterfaceMeta(type):
    def __new__(cls, name, bases, dct):
        for key, value in dct.items():
            if not key.startswith('__') and inspect.isfunction(value):
                value = t_interface(True)(value)
                dct[key] = value

        return type.__new__(cls, name, bases, dct)


def make_noconflict_metaclass(cate='trace'):
    metaclass = {'trace': TraceMeta,
                 'interface': InterfaceMeta}.get(cate)
  

    def noconflict_metaclass(name, bases, dct):
        meta_set = set()
        for base in bases:
            if '__metaclass__' in dir(base):
                meta_set.add(getattr(base, '__metaclass__'))
        meta_set = [ metaclass ] + list(meta_set)
        MixMeta = type('MixMeta', tuple(meta_set), {})

        return MixMeta(name, bases, dct)

    return noconflict_metaclass

