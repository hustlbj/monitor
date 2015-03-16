import os
import time

QUEUE_LOG_DIR = "/tmp/queue_log"

LOG_FORMAT = "[%(time)s] [%(identity)s] [%(information)s]"

class Logger(object):

    def __init__(self,logger_file,file_dir=None):

        if not os.path.isdir(QUEUE_LOG_DIR):
            os.mkdir(QUEUE_LOG_DIR)

        if not file_dir:
            self._dir = QUEUE_LOG_DIR

        self._dir = QUEUE_LOG_DIR + "/" + file_dir

        if not os.path.isdir(self._dir):
            os.mkdir(self._dir)

        self._create_logger_file(logger_file)

    def _create_logger_file(self,logger_file):
        t = time.ctime(time.time())
        """the sentence annotated is the old one"""
        #t = t.split(' ')
        t = t.split()
        assert len(t) == 5
        t = t[4]+'_'+t[1]+'_'+t[2]#year_month_day


        self._file_name = logger_file + "_" + t + ".log"

        full_name = self._dir+"/"+self._file_name
        if not os.path.exists(full_name):
            os.mknod(full_name)

        self.fp = open(full_name,'a')



    def logging(self,msg , identity =  None):
        record = {}
        record["time"] = time.ctime(time.time())
        record["information"] = msg

        if not identity:
            identity = ""

        record["identity"] = identity

        message = LOG_FORMAT % record

        message = message + "\n"

        self.fp.write(message)
        self.fp.flush()

    def close(self):
        self.fp.close()

