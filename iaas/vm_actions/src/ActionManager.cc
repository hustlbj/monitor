/*
 * ActionManager.cc
 *
 *  Created on: Jun 4, 2012
 *      Author: Wuxl
 */

#include"ActionManager.h"

void * action_loop(void* arg)
{

	ActionManager * am	= static_cast<ActionManager*>(arg);
	am->loop(am->loop_timer);
	return 0;

}

ActionManager::ActionManager(MySqlDB *db,int limit,time_t timer,const string & logfile)
{
	pthread_mutex_init(&am_mutex,0);
	pthread_cond_init(&am_cond,0);

	_signature = "A:sss";

	log = new FilelogTS(logfile);
	actions = new Actions(db,log);
	scheduler_limit = limit;
	loop_timer = timer;

	actions->select();

}

void ActionManager::loop(time_t timer)
{
	timespec timeout;
	int finalize	=	0;

	timeout.tv_sec = time(NULL)+timer;
	timeout.tv_nsec = 0;
	while(finalize == 0){

		pthread_mutex_lock(&am_mutex);

		pthread_cond_timedwait(&am_cond,&am_mutex,&timeout);


		if(actions->_actions.size()!=0){

#ifdef MQDEBUG
			PDEBUG("[ActionManager] Scheduler!\n");
#else
			log->log("[ActionManager] Scheduler");
#endif

			scheduler();
		}
		else
		{

#ifdef MQDEBUG
			PDEBUG("[ActionManager] Waiting for the next timeout!\n");
#else
			log->log("[ActionManager] Waiting for the next timeout");
#endif
		}

		pthread_mutex_unlock(&am_mutex);

		timeout.tv_sec = time(NULL)+timer;
		timeout.tv_nsec = 0;
	}
}

void ActionManager::scheduler()
{
	int sc_vms	= 0;
	int rc 		= 0;
	Action * action;
	const list<Action*>	_acitons = actions->_actions;
	list<Action*>::const_iterator	it;


	for(it = actions->_actions.begin();
		it !=actions->_actions.end() && sc_vms < scheduler_limit; it++)
	{
		rc = actions->dispatch(*it);
		if(rc!=0){
			// operation fail
		}
		sc_vms++;
	}

	while(sc_vms>0){
		action = actions->_actions.front();
		actions->_actions.pop_front();
		delete action;
		sc_vms--;
	}
}

void ActionManager::start()
{
	int rc = pthread_create(&start_thread,NULL,action_loop,(void *)this);
	if(rc !=0){

#ifdef MQDEBUG
		PDEBUG("[ActionManager] start pthread Error\n");
#else
		log->log("[ActionManager] start pthread Error!");
#endif

	}
	else
	{

#ifdef MQDEBUG
		PDEBUG("[ActionManager] Start pthread\n");
#else
		log->log("[ActionManager] Start pthread");
#endif

	}
}

void ActionManager::wait()
{
	pthread_join(start_thread,0);
}

void ActionManager::execute(xmlrpc_c::paramList const & paramList,
		xmlrpc_c::value * const retvalP)
{
	string username;
	string vmid;
	string action;
	string ip;

	int rc;

	vector<xmlrpc_c::value>		arrayData;
	xmlrpc_c::value_array *		arrayResult;

	username	= xmlrpc_c::value_string(paramList.getString(0));
	action		= xmlrpc_c::value_string(paramList.getString(1));
	vmid		= xmlrpc_c::value_string(paramList.getString(2));
	ip		= xmlrpc_c::value_string(paramList.getString(3));	

	pthread_mutex_lock(&am_mutex);

	rc = actions->troggler(username,action,vmid,ip);

	pthread_mutex_unlock(&am_mutex);

	if(rc==0){
		arrayData.push_back(xmlrpc_c::value_boolean(true));
		arrayData.push_back(xmlrpc_c::value_string("Task has been submit"));
	}
	else
	{
		arrayData.push_back(xmlrpc_c::value_boolean(false));
		arrayData.push_back(xmlrpc_c::value_string("Error"));
	}



	arrayResult = new xmlrpc_c::value_array(arrayData);

	*retvalP = *arrayResult;

	delete	arrayResult;

	return;
}


