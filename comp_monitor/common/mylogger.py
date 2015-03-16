#!/usr/bin/python

import logging

INFO = logging.INFO
DEBUG = logging.DEBUG
WARNING = logging.WARNING
ERROR = logging.ERROR

def getlogger(name, output = None, level = INFO):
	logger = logging.getLogger(name)
	logger.setLevel(level)
	handler = logging.StreamHandler() if level == logging.DEBUG else logging.FileHandler(output)
	formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	return logger
