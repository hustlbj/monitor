/*
 * ActionManager.h
 *
 *  Created on: Jun 4, 2012
 *      Author: Wuxl
 */

#ifndef ACTIONMANAGER_H_
#define ACTIONMANAGER_H_

#include"Actions.h"
#include"Log.h"
#include"MySqlDB.h"

#include<xmlrpc-c/registry.hpp>


class ActionManager: public xmlrpc_c::method
{
public:
	ActionManager(MySqlDB *db,int limit,time_t timer,const string & logfile);
	virtual ~ActionManager(){};

	void loop(time_t timer);

	void start();

	void scheduler();

	friend void * action_loop(void* arg);

	void wait();

	void execute(xmlrpc_c::paramList const & paramList,
					xmlrpc_c::value * const retvalP);

private:
	Actions *actions;
	pthread_mutex_t		am_mutex;
	pthread_cond_t		am_cond;
	int					scheduler_limit;
	time_t				loop_timer;
	pthread_t			start_thread;

	FilelogTS			*log;

};


#endif /* ACTIONMANAGER_H_ */
