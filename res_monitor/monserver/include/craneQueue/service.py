import sys, os , atexit
from signal import SIGTERM

class Service(object):

	def __init__(self,
		pidfile,
		stdin='/dev/null',
		stdout='/dev/null',
		stderr='/dev/null'):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = pidfile

	def _daemonize(self):
		"""
		double-fork daemonize
		"""
		pid = os.fork()
		if pid < 0:		#error
			sys.stderr.write("fork failed\n")
			sys.exit(1)
		elif pid > 0:	#parent
			sys.exit(0)


		#child
		os.setsid()
		os.chdir("/")
		os.umask(0)

		pid = os.fork()
		if pid < 0:
			sys.exit(1)
		elif pid > 0: #parent
			sys.exit(0)

		#child
		si = file(self.stdin,'r')
		so = file(self.stdout,'a+')
		se = file(self.stderr,'a+')

		os.dup2(si.fileno(),sys.stdin.fileno())
		os.dup2(so.fileno(),sys.stdin.fileno())
		os.dup2(se.fileno(),sys.stdin.fileno())

		atexit.register(self._del_pidfile)
		pid = str(os.getpid())
		fp = file(self.pidfile,'w+')
		fp.write("%s\n"%pid)
		fp.close()

	def _del_pidfile(self):
		os.remove(self.pidfile)

	def _check_pidfile(self):
		try:
			fp = file(self.pidfile,'r')
			pid = int(fp.read().strip())
			fp.close()
		except IOError:
			pid = None

		return pid

	def _run(self,agent):
		agent.start_consuming()

	def start(self,agent):
		pid = self._check_pidfile()

		if pid:
			sys.stdout.write("%s is running. Or remove %s\n"%(pid,self.pidfile))
			sys.stdout.flush()
			sys.exit(1)

		self._daemonize()
		self._run(agent)

	def stop(self):
		pid = self._check_pidfile()

		if not pid:
			sys.stdout.write("No Such Process")
			sys.stdout.flush()
			sys.exit(1)

		try:
			os.kill(pid, SIGTERM)
		except OSError,err:
			rlt = str(err)
			if rlt.find("No sucn process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				sys.exit(1)
		if os.path.exists(self.pidfile):
			os.remove(self.pidfile)

	def restart(self,agent):
		self.stop()
		self.start(agent)

