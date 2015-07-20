from IaaSAPI import IaaSAPI
import time
import random
import json

conf={}
conf["DIRECT_EXCHANGE"] = "call_direct_topic"
conf["TOPIC_EXCHANGE"] = "service_call_topic"
conf["RPC_EXCHANGE"] = "service_cast_topic"

iaas_api = IaaSAPI(conf,'iaas_api')

print iaas_api.get_hostpool_info()

