/*
 * ObjectSql.h
 *
 *  Created on: Apr 22, 2012
 *      Author: Wuxl
 */

#ifndef OBJECTSQL_H_
#define OBJECTSQL_H_

#include "Callbackable.h"
#include "SqlDB.h"

class ObjectSql : public Callbackable{
public:
	ObjectSql(){};

	virtual ~ObjectSql(){};

protected:
	virtual int select(SqlDB *db) = 0;

	virtual int insert(SqlDB *db) = 0;

	virtual int update(SqlDB *db) = 0;

	virtual int drop(SqlDB *db) = 0;

};



#endif /* OBJECTSQL_H_ */
