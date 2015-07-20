/*
 * SqlDB.h
 *
 *  Created on: Apr 21, 2012
 *      Author: Wuxl
 */

#ifndef SQLDB_H_
#define SQLDB_H_

#include <string>
#include <sstream>

#include "Callbackable.h"

using namespace std;

class SqlDB{
public:
	SqlDB(){};

	virtual ~SqlDB(){};

	virtual int exec(stringstream &cmd, Callbackable* obj =0) = 0;

	virtual char * escape_str(const string & str) = 0;

	virtual void free_str(char * str) = 0;
};



#endif /* SQLDB_H_ */
