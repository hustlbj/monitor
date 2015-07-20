/*
 * Actions.h
 *
 *  Created on: Jun 4, 2012
 *      Author: Wuxl
 */

#ifndef ACTIONS_H_
#define ACTIONS_H_

#include <list>
#include"Callbackable.h"
#include"MySqlDB.h"
#include"Log.h"
#include"ONEClient.h"
#include<unistd.h>
#include<string.h>
#include<stdlib.h>
#include<stdio.h>
using namespace std;

struct Action{
	string	_username;
	string	_action;
	string	_vmid;
	string _ip;
	int		_oid;
	Action(	const string& username,
			const string& action,
			const string &vmid)
	{
		_username	= username;
		_action   	= action;
		_vmid		= vmid;
	}
};


class Actions : Callbackable{
public:
	Actions(MySqlDB * db,FilelogTS * log);
	virtual ~Actions();

	int cb_select(int num, char ** values, char **name);

	int select();

	int insert(Action * action);

	int troggler(const string & username,
				 const string & act,
				 const string & vmid,
				 const string & ip);

	int update(Action * action,int rls);

	int dispatch(Action * action);


	friend class ActionManager;
private:
	list<Action*>	_actions;
	MySqlDB*		_db;
	FilelogTS*		_log;
	ONEClient*		_client;

};


#endif /* ACTIONS_H_ */
