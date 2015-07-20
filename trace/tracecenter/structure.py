#!/usr/bin/env python

TIMEOUT = 20
DELAY = 5

class Trace(object):
    
    def __init__(self, obj):
        self.id = obj.pop('trace')
        self.trace = [obj]
        self.imcomplete = 1

    def add(self, obj):
        obj.pop('trace')
        self.trace.append(obj)
        self.imcomplete += 1

    def complement(self, obj):
        obj.pop('trace')
        for item in self.trace:
            if item['current'] == obj['current'] and item['start'] == obj['start']:
                item.update(obj)
                self.imcomplete -= 1
                break

    @property
    def is_complete(self):
        return not self.imcomplete

    @property
    def is_failed(self):
        return not self.imcomplete and not self.head.get('state', True)

    def is_valid(self):
        head = min(self.trace, key=lambda x:x['start'])
	print head
        if head.has_key('params'):
            self.head = head
            return True
        else:
            return False


    def sort(self):
        self.trace.sort(lambda x,y: x['start']-y['start']>=0 and 1 or -1)

    def format(self):
        self.time = self.trace[0]['start']
        self.key = self.trace[0]['current']

        temp = []
        for i, item in enumerate(self.trace):
            edge = (item['last'], item['current'])
            if edge not in temp:
                temp.append(edge)

            #if not self.imcomplete:
            try:
                item['cost'] = (item['end']-item['start'])*1000
                i-=1
                while i>=0:
                    if self.trace[i]['current']==item['last']:
                        self.trace[i]['cost'] -= item['cost']
                        break
                    i-=1
            except Exception, err:
                continue     

        self.overview = []
        for item in temp:
            self.overview.append({'last':item[0], 'current':item[1]})

        del temp

    def dump(self):
        return {'id': self.id, 'trace': self.trace}

