#!/usr/bin/env python
import sys
import os
import signal
import time

class Launcher:
	"""
	Implement common operation on service.
	"""

	def __init__(self, service, binary):
		self.service = service
		self.binary = binary


	def start(self):
		"""
		Start service.		
		"""
	
		# First fork
		try:
			pid = os.fork()
			if pid>0:
				sys.exit(0)
		except OSError, e:
			sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
			sys.exit(1)
	
		# os.chdir("/")
		os.umask(0)
		os.setsid()
	
		# Second fork
		try:
			pid = os.fork()
			if pid > 0:
				print "Process: %d" % pid
				sys.exit(0)
		except OSError, e:
			sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
			sys.exit(1)
	
	
	
		# Launch service
		# redirect standard stream to /dev/null
		stdin, stdout, stderr = 0, 1, 2
		si = open("/dev/null", 'r')
		so = open("/dev/null", 'a+')
		se = open("/dev/null", 'a+', 0)
		os.dup2(si.fileno(), stdin)
		os.dup2(so.fileno(), stdout)
		os.dup2(se.fileno(), stderr)
	
		# import binary
		mod_str, cls_str = self.binary.rsplit('.', 1)
		__import__(mod_str)
		module = sys.modules[mod_str]
		cls = getattr(module, cls_str)
	
		service = cls()

		# handle TERMINAL singnal to release source while exiting. 
		def handle_signal(signo, frame):
			service.stop()
	
		signal.signal(signal.SIGTERM, handle_signal)

		# run service and wait for exiting
		try:	
			service.start()
			service.wait()
		except Exception, e:
			from logger import getlogger

			logger = getlogger("Main")
			logger.error(str(e))
	
		# Release source
		si.close()
		so.close()
		se.close()
	

	def _getpid(self):
		"""
		Get Process ID of running service.

		:returns: process id if service running, 0 otherwise.
		"""

		ret = os.popen("ps aux|grep '%s start'|grep -v grep"%self.service).readlines()
		if len(ret):
			pid = int(ret[0].split()[1])
			return pid
	
		return 0
	
		
	
	def stop(self):
		"""
		Stop service.

		:returns: True if service running, False otherwise
		"""

		pid = self._getpid()
	
		if not pid:
			print "%s is not running" % self.service
			return False
			
		os.kill(pid, signal.SIGTERM)
		print "stopping %s ..." % self.service

		time.sleep(3)
		return True
	

	def restart(self):
		"""
		Restart service.
		"""

		if self.stop():
			self.start()

	
	def help(self):
		"""
		Print help infomation.
		"""

		print "Usage: %s {start|stop|restart}" % self.service
		print 



if __name__=="__main__":
	l = Launcher('fda', 'minf')
	print l._getpid()
	#start("monitor.monserver.monserver.MonServer")

