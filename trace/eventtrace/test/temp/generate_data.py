#!/usr/bin/env python

import random
import time
import uuid
import pprint

def generate_cluster_data(m, n):
    base = []
    for i in range(m):
        temp = []
        for i in range(3):
            temp.append(random.uniform(0, 300))
        base.append(temp)
    pprint.pprint(base)

    result = []
    for i in range(n):
        trace = []
        trace_id = str(uuid.uuid4())
        for j in range(m):
            t = random.choice(base[j])
            tt = random.uniform(t-30, t+30)
            while tt<0:
                tt = random.uniform(t-30, t+30)
            entry = {'trace': trace_id, 'time': tt, 'start': time.time(), 'end': time.time()+tt, 'com': j}
            trace.append(entry)

        result.append(trace)

    return result
        
    

if __name__=="__main__":
    pprint.pprint(generate_cluster_data(5, 20)    )
