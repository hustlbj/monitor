/*
 * mq.h
 *
 *  Created on: Jun 4, 2012
 *      Author: Wuxl
 */

#ifndef MQ_H_
#define MQ_H_
#include<stdlib.h>
#include<stdio.h>

#undef	PDEBUG
#ifdef	MQDEBUG
#	define	PDEBUG(fmt,args...)		printf(fmt,##args)
#else
#	define	PDEBUG(fmt,args...)
#endif


#ifndef MAX_ROW
#define	MAX_ROW	6
#endif

#define OID_INDEX		0
#define	UNAME_INDEX		1
#define ACTION_INDEX	2
#define VM_INDEX		3

#include<string>
#include <sstream>

#endif /* MQ_H_ */
