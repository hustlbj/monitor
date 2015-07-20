/*
 * Callbackable.h
 *
 *  Created on: Jun 4, 2012
 *      Author: Wuxl
 */

#ifndef CALLBACKABLE_H_
#define CALLBACKABLE_H_

#include<pthread.h>
#include"mq.h"

class Callbackable{
public:
	Callbackable(){
		pthread_mutex_init(&_cb_mutex,0);
	}

	virtual ~Callbackable(){
		pthread_mutex_destroy(&_cb_mutex);
	}

	typedef	int(Callbackable::*Callback)(int num,char ** values, char ** names);

	void set_callback(Callback cb){
		pthread_mutex_lock(&_cb_mutex);
		_cb = cb;
	}

	void unset_callback(){
		_cb = 0;
		pthread_mutex_unlock(&_cb_mutex);
	}

	int do_callback(int num,char** values, char**names){
		return (this->*_cb)(num, values, names);
	}

	int isCallbackSet(){
		return (_cb != 0);
	}

private:
	pthread_mutex_t	_cb_mutex;
	Callback		_cb;
};


#endif /* CALLBACKABLE_H_ */
