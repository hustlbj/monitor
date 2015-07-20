/*
 * MySqlDB.cc
 *
 *  Created on: Apr 22, 2012
 *      Author: Wuxl
 */

#include "MySqlDB.h"
#include <mysql/errmsg.h>
#include <iostream>
using std::cout;
using std::endl;



MySqlDB::MySqlDB(const string &_server,
		int _port,
		const string & _user,
		const string & _password,
		const string & _database,
		const string&	_logfile)
{
	server	 = _server;
	port	 = _port;
	user	 = _user;
	password = _password;
	database = _database;

	log = new FilelogTS(_logfile);

	//Initialize the MYSQL library
	mysql_library_init(0,NULL, NULL);

	db = mysql_init(NULL);

	if(!mysql_real_connect(db,server.c_str(),user.c_str(),password.c_str(), database.c_str(),port,NULL,0)){
		//cloud not open databases;
		cout<<"connect error"<<endl;
	}

	pthread_mutex_init(&mutex,0);

}

MySqlDB::~MySqlDB()
{
	mysql_close(db);

	mysql_library_end();

	pthread_mutex_destroy(&mutex);
}


int MySqlDB::exec(stringstream & cmd, Callbackable *obj){
	int rc;

	const char * c_str;

	string str = cmd.str();
	c_str = str.c_str();

	lock();

	rc = mysql_query(db,c_str);

	if (rc != 0)
	{
		stringstream ss;
	    const char *    err_msg = mysql_error(db);
	    int             err_num = mysql_errno(db);

	    if( err_num == CR_SERVER_GONE_ERROR || err_num == CR_SERVER_LOST )
	    {
	    	log->log("MySQL connection error ");

	        // Try to re-connect
	        if (mysql_real_connect(db, server.c_str(), user.c_str(),
	                                    password.c_str(), database.c_str(),
	                                    port, NULL, 0))
	        {
	        	log->log("... Reconnected.");
	        }
	        else
	        {
	        	log->log("... Reconnection attempt failed.");
	        }
	     }
	     else
	     {
	    	  ss<<"SQL command was: " <<c_str<<", error "<<err_num<<" : " << err_msg;
	    	  log->log(ss.str());
	     }

	     unlock();

	     return -1;
	}


	if((obj!=0) && (obj->isCallbackSet())){
		// select
		MYSQL_RES *		res_ptr;
		MYSQL_ROW 		row;
		MYSQL_FIELD *	fields;

		unsigned int num_fields;

		res_ptr = mysql_store_result(db);

		if(res_ptr == NULL){
			cout<<"mysql_store_result error"<<endl;
		}


		num_fields	= mysql_num_fields(res_ptr);
		fields		= mysql_fetch_fields(res_ptr);

		char ** names = new char*[num_fields];
		for(unsigned int i = 0; i< num_fields; i++){
			names[i] = fields[i].name;
		}


		while((row = mysql_fetch_row(res_ptr))){
			obj->do_callback(num_fields,row,names);
		}

		mysql_free_result(res_ptr);
		delete [] names;

	}else
	{
		rc = mysql_query(db,"SELECT LAST_INSERT_ID()");
		if(rc){
			log->log("SELECT LAST_INSERT_ID error");
		}else
		{
			MYSQL_RES *		res_ptr;
			MYSQL_ROW 		row;
			res_ptr = mysql_use_result(db);
			if(res_ptr){
				while((row = mysql_fetch_row(res_ptr))){
					rc = atoi(row[0]);
				}
			}
			mysql_free_result(res_ptr);
		}
	}
	unlock();

	return rc;
}

char * MySqlDB::escape_str(const string & str)
{
	char * result = new char[str.size()];

	mysql_real_escape_string(db,result,str.c_str(),str.size());

	return result;
}

void MySqlDB::free_str(char * str)
{
	delete [] str;
}



