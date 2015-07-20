/*
 * Actions.cc
 *
 *  Created on: Jun 4, 2012
 *      Author: Wuxl
 */

#include"Actions.h"


Actions::Actions(MySqlDB * db,FilelogTS * log)
{
	_db	= db;
	_log = log;

	//_client = new ONEClient(2633,"202.114.10.146");
	_client = new ONEClient(2633,"localhost",log);
}

Actions::~Actions()
{
}

int Actions::cb_select(int num,char** values,char** name)
{
	int rc;
	if(num!=MAX_ROW)
	{
#ifdef MQDEBUG
		PDEBUG("Read Database Error\n");
#else
		_log->log("Read Database Error");
#endif
		return -1;
	}

	if(values[UNAME_INDEX]==NULL || values[ACTION_INDEX]==NULL || values[VM_INDEX]==NULL){

#ifdef MQDEBUG
		PDEBUG("Action Request  NULL\n");
#else
		_log->log("Action Request  NULL");
#endif
		return -1;
	}

	Action *action = new Action(values[UNAME_INDEX],
								values[ACTION_INDEX],
								values[VM_INDEX]);
	action->_oid = atoi(values[OID_INDEX]);

	_actions.push_back(action);

	return rc;
}

int Actions::select()
{
	int rc;
	stringstream ss;

	set_callback(static_cast<Callbackable::Callback>(&Actions::cb_select));

	ss<<"SELECT * FROM virtual_machine_action WHERE _finished = 0";

	rc = _db->exec(ss,this);

	unset_callback();

	return rc;
}

int Actions::update(Action *action, int rls){
	int rc;
	stringstream ss;

	if(rls == 0)
	{
		ss<<"UPDATE virtual_machine_action SET _finished = 1 , _succeeded = 1 WHERE oid = "<<action->_oid;
	}else
	{
		ss<<"UPDATE virtual_machine_action SET _finished = 1 , _succeeded = 0 WHERE oid = "<<action->_oid;
	}


#ifdef MQDEBUG
	PDEBUG(ss.str().c_str());
	PDEBUG("\n");
#else
	_log->log(ss.str());
#endif

	rc = _db->exec(ss,this);

	return rc;
}
int Actions::insert(Action * action)
{
	int rc;
	stringstream ss;

	_actions.push_back(action);

	ss<<"INSERT INTO virtual_machine_action (_username,_action,_vmid,_finished,_succeeded) VALUES('"
				<<action->_username<<"','"
				<<action->_action<<"','"
				<<action->_vmid<<"',"
				<<0<<","
				<<0<<")";
#ifdef MQDEBUG
	PDEBUG(ss.str().c_str());
	PDEBUG("\n");
#else
	_log->log(ss.str().c_str());
#endif

	rc = _db->exec(ss,this);

	return rc;
}

int Actions::dispatch(Action *action)
{
	int rc = 0;

#ifdef MQDEBUG
	PDEBUG("[Actions] %s Vm is %sed by %s\n",action->_vmid.c_str(),action->_action.c_str(),action->_username.c_str());
#else
	_log->log("[Actions] "+action->_vmid+" VM is "+action->_action+"ed by "+action->_username);
#endif

	// send the request to OpenNebula
#ifdef MQDEBUG
	PDEBUG("_client->do_action\n");
#else
	rc = _client->do_action(action->_username,action->_action,action->_vmid);
#endif

	if(rc!=0){
		//error
	}
	// shutdown the vm ignore the error 
/*
	if((rc == 0)&&(action->_action == "shutdown" || action->_action == "stop")){
		_log->log("[Actions]"+action->_action+" VM with shutdown shell");
		FILE * fp;
		char buffer[2048+1];
		int chars_read;
		stringstream ss;
		ss<<"ssh root@"<<action->_ip<<" shutdown -h 2 &";
#ifdef	MQDEBUG
		PDEBUG(ss.str().c_str());
		PDEBUG("\n");
#else	
		_log->log(ss.str());
#endif
		memset(buffer,0,sizeof(buffer));
		fp = popen(ss.str().c_str(),"r");	
#ifndef MQDEBUG
		_log->log("popen function over");
#endif
		if(fp != NULL)
		{
			chars_read = fread(buffer,sizeof(char),2048,fp);
			if(chars_read > 0){
#ifdef MQDEBUG
				PDEBUG(buffer);
				PDEBUG("\n");
#else
				_log->log("fread over !");
				_log->log(buffer);
#endif
			}
			pclose(fp);
		}
		else
		{
#ifdef MQDEBUG
			PDEBUG("[Actions] popen error");
#else
			_log->log("[Actions] popen error !");
#endif
		}
	}
*/	
	update(action,rc);




	return rc;
}

int Actions::troggler(const string & username,
		const string & act,
		const string & vmid,
		const string & ip)
{
	int rc;
	Action * action = new Action(username,act,vmid);
	action->_ip = ip;
	rc = insert(action);
	action->_oid = rc;


	if(rc < 0){

#ifdef MQDEBUG
		PDEBUG("[Actions] %s Vm %s Insert Actions Error\n",action->_vmid.c_str(),action->_action.c_str());
#else
		_log->log("[Actions]"+action->_vmid+" Vm "+action->_action+" Insert Actions Error");
#endif

		return 1;
	}

	return 0;
}

