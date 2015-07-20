import IaaSAPI

conf = {}
conf['DIRECT_EXCHANGE'] = 'call__direct_topic'
conf['TOPIC_EXCHANGE'] = 'service_call_topic'
conf['RPC_EXCHANGE'] = 'service_cast_topic'

op = IaaSAPI.IaaSAPI(conf, 'iaas_api')

rlts = op.get_vmpool_info("test")
print rlts
