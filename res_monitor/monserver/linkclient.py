import socket
import pprint
import json
import time
from linkhust import MongoDB
from common.package import Package
from configobj import ConfigObj
import os
import os.path as path

CONF_PATH = '/usr/crane/package/conf/webpaas.conf'
config = ConfigObj(CONF_PATH)

dns = config['dns']
site = dns['appDomain'].split('.')[0]

root_dir = path.dirname(path.abspath(__file__)) + path.sep
CONF = ConfigObj(root_dir+"server.conf")
conf_db = CONF['db']

mongo_host = conf_db['addr']
mongo_port = conf_db.as_int('port')
server_host = "202.114.10.168"
server_port = 9527
sleep_time = 60

print mongo_host
print mongo_port

while(True):
    time.sleep(sleep_time)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect((server_host, server_port))
        db = MongoDB((mongo_host, mongo_port), "monitor_fine_grained", "metadata")
        data = (site, db.dump_metric(db.get_hosts(), (-sleep_time, None)).items())
        for hosttuple in data[1]:
            dictlist = hosttuple[1]
            for diction in dictlist:
                diction['_id'] = str(diction['_id'])
        pack = Package('DATA', json.dumps(data))
        server.send(pack.serialize())
        server.close()
    except Exception, e:
        print e
        continue
