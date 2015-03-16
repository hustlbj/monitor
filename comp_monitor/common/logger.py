#!/usr/bin/env python

import logging
import logging.config
import sys
import os.path as path

__all__ = ['config_logging', 'getlogger']


# Basic logging config information
LOGGING_CONF = {
	'version': 1,
	'disable_existing_loggers': False,

	# declare formatters
	'formatters': { 
	    'verbose': {
	        'format': '[%(levelname)s] %(asctime)s - %(module)s.%(name)s: %(message)s'
	    },
	    'simple': {
	        'format': '[%(levelname)s] %(module)s: %(message)s'
	    },
	},

	# declare handlers
	'handlers': { 
		'console': {
			'class': 'logging.StreamHandler',
			'formatter': 'simple',
			'level': 'DEBUG',
			'stream': 'ext://sys.stdout'
		},
		'file': {
			'class': 'logging.handlers.RotatingFileHandler',
			'formatter': 'verbose',
			'level': 'INFO',
			'filename': 'monitor.log',
			'maxBytes': 5*2**20,
			'backupCount': 7, 
		},
	},

	# root logger
	'root': {
		'handlers': ['console', 'file'],
		'level': 'DEBUG',
		'propagate': True
	},
}

def config_logging(file=None):
	"""
	Config filename for file handler.
	"""

	if file:
		LOGGING_CONF['handlers']['file']['filename'] = file
	
	# Config logging using dictConfig directly if version greater than 2.7
	if sys.version >= '2.7':
		logging.config.dictConfig(LOGGING_CONF)


def getlogger(name):
	"""
	Get logger using basic logging.

	:returns: logger object.
	"""
	import logging
	if sys.version >= '2.7':
		return logging.getLogger(name)

	import logging.handlers

	level = {'DEBUG':logging.DEBUG, 'INFO':logging.INFO}

	logger = logging.getLogger(name)
	logger.setLevel(level[LOGGING_CONF['root']['level']])

	# create formatter
	formatters = {}
	for key, val in LOGGING_CONF['formatters'].items():
		formatters[key] = logging.Formatter(val['format'])

	# create file handler
	fh_conf = LOGGING_CONF['handlers']['file']
	fh = logging.handlers.RotatingFileHandler(fh_conf['filename'],
							'a',
							fh_conf['maxBytes'],
							fh_conf['backupCount'])
	fh.setLevel(level[fh_conf['level']])
	fh.setFormatter(formatters[fh_conf['formatter']])

	# create console handler
	ch_conf = LOGGING_CONF['handlers']['console']
	ch = logging.StreamHandler()
	ch.setLevel(level[ch_conf['level']])
	ch.setFormatter(formatters[ch_conf['formatter']])

	# add the handlers to logger
	logger.addHandler(ch)
	logger.addHandler(fh)	

	return logger


if __name__=="__main__":
	config_logging()
	logger = getlogger("xxx")
	print sys.version >= '2.7'

	import time
	while True:
		logger.debug("this is debug log")
		logger.info("this is info log")
		time.sleep(3)
