/*
 * Log.h
 *
 *  Created on: Apr 26, 2012
 *      Author: Wuxl
 */

#ifndef LOG_H_
#define LOG_H_

#include <string>
#include <fstream>

#include <string.h>
#include <pthread.h>

using namespace std;

class Filelog{
public:
	Filelog(const string & _filename);

	virtual ~Filelog(){};

	virtual void log(const string& message);

private:
	 char* filename;
};

class FilelogTS : public Filelog{
public:
	FilelogTS(const string & filename)
		:Filelog(filename)
	{
		pthread_mutex_init(&mutex,0);
	}

	virtual ~FilelogTS(){
		pthread_mutex_destroy(&mutex);
	}

	virtual void log(const string& message){
		pthread_mutex_lock(&mutex);
		Filelog::log(message);
		pthread_mutex_unlock(&mutex);
	}

private:
	pthread_mutex_t mutex;
};



#endif /* LOG_H_ */
