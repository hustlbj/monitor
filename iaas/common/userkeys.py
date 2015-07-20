#!/usr/bin/python

import commands
import MySQLdb
import gridfs
from pymongo import Connection
import os

if os.getenv('ONE_LOCATION'):
    ONE_LOCATION = os.getenv('ONE_LOCATION')
else:
    ONE_LOCATION = "/home/crane/chris/one"

KEY_DIR=''
dbuser=''
dbpasswd=''
keysdb=''
mongip=''
mongport=''
def createkeys(username,keyname):
	keydir=KEY_DIR+'/'+username+'/'+keyname
	keydircommand='mkdir -p '+keydir
	stat,output=commands.getstatusoutput(keydircommand)
	if stat!=0:
		return [stat,output]
	createcommand='ssh-keygen -q -t dsa -f '+keydir+'/id_dsa'+' -P ""'
	stat,output=commands.getstatusoutput(createcommand)
	commands.getstatusoutput('chown -R crane:crane '+keydir)
	return [stat,output]
def deletekeys(username,keyname):
	keydir=KEY_DIR+'/'+username+'/'+keyname
	delcommand='rm -rf '+keydir
	stat,output=commands.getstatusoutput(delcommand)
	return [stat,output]

#if the key is avaible,return [0,GridOut],else[1,'fail info']
def downloadkeys(username, keyname):
    try:
        connect = "mongodb://" + str(mongip) + ":" + str(mongport) + "/"
        fs = gridfs.GridFS(Connection(host = connect).gridfs,collection=username)
        if fs.exists(filename = keyname):
            return [0, fs.get_last_version(keyname).read()]
        else:
            return [1,'userkey not exist!']
    except:
        return [1,'Mongodb error!']

def checkfsexist(username,keyname):
        try:
                connect = "mongodb://" + str(mongip) + ":" + str(mongport) + "/"
                fs = gridfs.GridFS(Connection(host = connect).gridfs,collection=username)
                if fs.exists(filename=keyname):
			return [1,'the file '+keyname+'  has already exists in gridfs']
                else:
			return [0,'success']
        except:
                return [1,'fail']

def getfromgrid(username,keyname):
        keydir=KEY_DIR+'/'+username+'/'+keyname
        keydircommand='mkdir -p '+keydir
        stat,output=commands.getstatusoutput(keydircommand)
        if stat!=0:
                return [stat,output]
        try:
                connect = "mongodb://" + str(mongip) + ":" + str(mongport) + "/"
                fs = gridfs.GridFS(Connection(host = connect).gridfs,collection=username)
                keypath=keydir+'/id_dsa'
		fp=open(keypath,'w')
		fp.write(fs.get_last_version(keyname).read())
		fp.close()
                keypathpub=keydir+'/id_dsa.pub'
		fp=open(keypathpub,'w')
                fp.write(fs.get_last_version(keyname+'_pub').read())
                fp.close()
                return [0,'success']
        except:
                return [1,'cp to local fail']

def put2fs(username,keyname):
	try:
		connect = "mongodb://" + str(mongip) + ":" + str(mongport) + "/"
		fs = gridfs.GridFS(Connection(host = connect).gridfs,collection=username)
		keypath=KEY_DIR+'/'+username+'/'+keyname+'/id_dsa'
		fs.put(file(keypath),filename=keyname)
		keypathpub=KEY_DIR+'/'+username+'/'+keyname+'/id_dsa.pub'
		fs.put(file(keypathpub),filename=keyname+'_pub')
		return [0,'success']
	except:
		return [1,'put to grid fail']
def del2fs(username,keyname):
    try:
        connect = "mongodb://" + str(mongip) + ":" + str(mongport) + "/"
        fs = gridfs.GridFS(Connection(host = connect).gridfs,collection=username)
        id = fs.get_last_version(keyname)._id
	fs.delete(id)
        id2 = fs.get_last_version(keyname+'_pub')._id
        fs.delete(id2)
        return [0,'success']
    except:
        return [1,'delete from grid fail']
def insertdb(username,keyname):
	try:
		conn=MySQLdb.connect(host='localhost',user=dbuser,passwd=dbpasswd,db=keysdb)
		cursor=conn.cursor()
		n=cursor.execute('insert into userkeys value(%s,%s)',(username,keyname))
		conn.commit()
	except MySQLdb.Error,e:
		cursor.close()
		conn.close()
		return [1,'insert to db fail']
	cursor.close()
	conn.close()
	return [0,'success']
def delfromdb(username,keyname):
	try:
	        conn=MySQLdb.connect(host='localhost',user=dbuser,passwd=dbpasswd,db=keysdb)
       		cursor=conn.cursor()
	        n=cursor.execute('delete from  userkeys where user_name=%s and key_name=%s',(username,keyname))
		conn.commit()
	except MySQLdb.Error,e:  
     		cursor.close()
        	conn.close()
		return [1,'delete from db fail']
	cursor.close()
	conn.close()
        return [0,'success']
def usercreatekeys(username,keyname):
        dbcheck=checkdbexist(username,keyname)
        if dbcheck[0]!=0:
                return dbcheck
	exis=checkfsexist(username,keyname)
	if exis[0]!=0:
		cpfromgrid=getfromgrid(username,keyname)
		if cpfromgrid[0]!=0:
			return cpfromgrid
	else:
        	cmdout=createkeys(username,keyname)
       		if cmdout[0]!=0:
                	return cmdout
		put2fs(username,keyname)
	dbout=insertdb(username,keyname)
	return dbout
def userdelkeys(username,keyname):
	if keyname.strip()=='':
		return [1,'the keyname is empty']
	cmdout=deletekeys(username,keyname)
        if cmdout[0]!=0:
                return cmdout
	if checkfsexist(username,keyname)[0]==1:
		del2fs(username,keyname)
        dbout=delfromdb(username,keyname)
        return dbout
def checkdbexist(username,keyname):
        try:
                conn=MySQLdb.connect(host='localhost',user=dbuser,passwd=dbpasswd,db=keysdb)
                cursor=conn.cursor()
                cursor.execute(' select * from userkeys where user_name=%s and key_name=%s',(username,keyname))
                result=cursor.fetchall()
        except MySQLdb.Error,e:
                cursor.close()
                conn.close()
                return [False,e]
	if len(result)==0:
		return [0,'the name can use']
	else:
		return [1,'the name '+keyname+' has already exists']
def querykeys(username):
	try:
        	conn=MySQLdb.connect(host='localhost',user=dbuser,passwd=dbpasswd,db=keysdb)
	        cursor=conn.cursor()
        	cursor.execute(' select * from userkeys where user_name=%s',(username))
        	result=cursor.fetchall()
	except MySQLdb.Error,e:
		cursor.close()
       		conn.close()
		return [False,e]
        return [True,result]	



#the function bellow are used to the ocncentration and distribution fo user keys#first the key is created at the site of hust,then get the key contents and copy to other sites
#when user deletes keys, first delete at the site of hust, then delete from other sites
def getkeycontent(username, keyname, is_pub=None):
    if is_pub == True:
        keyname += '_pub'
    try:
        connect = "mongodb://" + str(mongip) + ":" + str(mongport) + "/"
        fs = gridfs.GridFS(Connection(host = connect).gridfs,collection=username)
        if fs.exists(filename = keyname):
            return [True, fs.get_last_version(keyname).read()]
        else:
            return [False,'userkey not exist!']
    except:
        return [True,'Mongodb error!']
    
def copykey2local(username, keyname, content, is_pub=None):
    #When read from mongodb,the last line is '\n',remove the line
    if content[-1] == '\n':
        content = content[0:-1]
    keydir=KEY_DIR+'/'+username+'/'+keyname
    keydircommand='mkdir -p '+keydir
    stat,output=commands.getstatusoutput(keydircommand)
    if stat!=0:
        return [False,output]
    if is_pub == True:
        keyfile=KEY_DIR+'/'+username+'/'+keyname+'/id_dsa.pub'
    else:
        keyfile=KEY_DIR+'/'+username+'/'+keyname+'/id_dsa'
    copycommand='echo "'+content+'" >> '+keyfile
    stat,output=commands.getstatusoutput(copycommand)
    if stat !=0:
        return [False,output]
    return [True,"copy key to local correct!"]


def deletekey2local(username, keyname):
    keydir=KEY_DIR+'/'+username+'/'+keyname
    delcommand='rm -rf '+keydir
    stat,output=commands.getstatusoutput(delcommand)
    if stat!=0:
        return [False, output]
    return [True,"delete key correct!"]

def getconfig():
	global KEY_DIR,dbuser,dbpasswd,keysdb,mongip,mongport
	configinfo={}
	file=open('/usr/crane/package/conf/iaasuserkeys.conf','r')
	for i in file.readlines():
		if i=='\n':
			continue
		if i[0]=='#':
			continue
		tmp=i.split('=')
		tmpname=tmp[0].strip()
		tmpdata=tmp[1][:-1].strip()
		configinfo[tmpname]=tmpdata
	KEY_DIR=ONE_LOCATION+'/share/scripts/userkeys'
	dbuser=configinfo['dbuser']
	dbpasswd=configinfo['dbpasswd']
	keysdb=configinfo['db']
	mongip=configinfo['mongip']
	mongport=configinfo['mongport']
	return configinfo
getconfig()
#print querykeys('itachi')
#print userdelkeys('itachi','key')
#print usercreatekeys('itachi','itachikey')
