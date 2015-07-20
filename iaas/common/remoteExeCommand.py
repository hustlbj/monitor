#!/usr/bin/python
import subprocess
import os
import sys
def cmd(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sts = os.waitpid(p.pid, 0)[1]
    ret = p.stdout.read()
    return (sts, ret)

def shutdown(host,user='root'):
    newcmd = "ssh %s@%s shutdown -h 'now'" % (user,host)
    ret = cmd(newcmd)
    return ret
