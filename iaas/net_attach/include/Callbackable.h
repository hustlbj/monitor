/*
 * Callbackable.h
 *
 *  Created on: Apr 21, 2012
 *      Author: Wuxl
 */

#ifndef CALLBACKABLE_H_
#define CALLBACKABLE_H_

#include <pthread.h>
/**
 *	Copy from OpenNebula
 */

class Callbackable{
public:
	Callbackable()
		:cb(0),arg(0)
	{
		pthread_mutex_init(&mutex,0);
	};

	virtual ~Callbackable(){
		pthread_mutex_destroy(&mutex);
	}

	typedef int (Callbackable::*Callback)(void *, int , char **, char **);

	void set_callback(Callback  _cb, void * _arg = 0){
		pthread_mutex_lock(&mutex);
		cb = _cb;
		arg = _arg;
	}

	void unset_callback(){
		cb = 0 ;
		arg = 0;
		pthread_mutex_unlock(&mutex);
	}

	int do_callback(int num, char ** values, char ** names){
		return (this->*cb)(arg, num , values, names);
	};

	int isCallbackSet(){
		return (cb != 0);
	}

private:
	Callback	cb;
	void *		arg;

	pthread_mutex_t	mutex;
};



#endif /* CALLBACKABLE_H_ */
