from eventtrace.import_utils import import_class
#from IaaSOperation import IaaSOperation
IaaSOperation = import_class("IaaSOperation.IaaSOperation")
api = IaaSOperation()
#print api.get_auth('test')
print api.get_hostpool_info()
