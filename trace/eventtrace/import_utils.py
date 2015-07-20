#!/usr/bin/env python

import inspect
from types import ClassType, FunctionType, BuiltinFunctionType
from injection import make_noconflict_metaclass, t_interface, t_trace


def _patch_class(cls, cate):
    class Temp(cls):
        __metaclass__ = make_noconflict_metaclass(cate)
    setattr(Temp, '__name__', cls.__name__)
    setattr(Temp, '__module__', cls.__module__)
    return Temp

def _patch_function(func, cate):
    trace_func = {'trace':t_trace, 
                  'interface':t_interface}[cate]
    return trace_func(False)(func)

def import_func(func, cate='trace'):
    return _patch_class(func, cate)

def import_class(class_path, cate='trace'):
    module_name, class_name = class_path.rsplit('.', 1)
    mod = __import__(module_name)
    print mod
    cls = getattr(mod, class_name)
    print cls

    return _patch_class(cls, cate)

def import_module(module_path, cate='trace'):
    modulelist = module_path.split('.')
    mod = __import__(module_path)
    for key in modulelist[1::]:
        mod = getattr(mod, key)
   
    for key,val in mod.__dict__.items():
        if not key.startswith('__'):
            if inspect.isclass(val) and (val.__module__ in module_path):
                if str(val.__class__) in ['xmlrpclib.ServerProxy']:
                    continue
                setattr(mod, key, _patch_class(val, cate)) 
            elif type(val) in [FunctionType, BuiltinFunctionType]:
                setattr(mod, key, _patch_function(val, cate))

    return mod
