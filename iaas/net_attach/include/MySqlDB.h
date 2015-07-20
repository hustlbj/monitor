/*
 * MySqlDB.h
 *
 *  Created on: Apr 21, 2012
 *      Author: Wuxl
 */

#ifndef MYSQLDB_H_
#define MYSQLDB_H_

#include "SqlDB.h"
#include "Log.h"
#include <mysql/mysql.h>



class MySqlDB : public SqlDB{
public:
	MySqlDB(const string&	_server,
		int		_port,
		const string&	_user,
		const string&	_passowrd,
		const string&	_database);
	virtual ~MySqlDB();

	int exec(stringstream &cmd, Callbackable* obj =0);

	char * escape_str(const string &str);

	void free_str(char *str);
private:
	MYSQL *		db;
	string		server;
	int 		port;
	string		user;
	string		password;
	string		database;

	pthread_mutex_t	mutex;

	FilelogTS * log;

	void lock()
	{
		pthread_mutex_lock(&mutex);
	}
	void unlock()
	{
		pthread_mutex_unlock(&mutex);
	}
};



#endif /* MYSQLDB_H_ */
