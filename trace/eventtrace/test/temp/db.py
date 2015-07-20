import pymongo

conn = pymongo.Connection("11.11.0.74", 27017)
db = conn['trace']
dbname = 'IaaSAPI-IaaSAPI.get_hostpool_info'
print dbname.rsplit('-')
coll = db[dbname]
#coll.update({'flag':'statistics'}, {'$inc':{'normal':3, 'timeout':0, 'failed':0}}, True)
print coll.find_one({'flag':'statistics'})
