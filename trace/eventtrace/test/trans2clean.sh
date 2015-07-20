#!/bin/bash

CRANE=/usr/crane/package/

python $CRANE/cloud/trace_iaas/IaaSAgent.py stop
cp $CRANE/lib/craneQueue/proxy_clean.py $CRANE/lib/craneQueue/proxy.py 
python $CRANE/cloud/clean_iaas/IaaSAgent.py start

