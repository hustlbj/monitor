#!/usr/bin/env python

import pymongo

class SchedAPI(object):

    def __init__(self, hostaddr, dbname):
        self.hostaddr = hostaddr
        self.dbname = dbname
        self.agent_set = []


    def get_agents(self):
        try:
            conn = pymongo.Connection(*hostaddr)
            db = conn[self.dbname]
            self.agent_set = db.collection_names()
            self.agent_set.remove('system.indexes')
        except pymongo.errors, e:
            pass
        return self.agent_set


    def get_metrics_day_to_day(self, col, start_t, end_t):
        try:
            conn = pymongo.Connection(*hostaddr)
            db = conn[self.dbname]
            return db[col].find({'day': {'$gte': self.date_to_stamp(start_t), \
                                '$lte': self.date_to_stamp(end_t)}})
        except pymongo.errors, e:
            return None


    def get_metrics_a_day(self, col, day):
        return self.get_metrics_day_to_day(col, str(day), str(day))


    def get_metrics_a_month(self, col, year, month):
        days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if (year % 4 == 0) or ((year % 100 == 0) and (year % 400 == 0)):
            days[1] = 29
        start_t = str(year) + '-' + str(month) + '-' + '1'
        end_t = str(year) + '-' + str(month) + '-' + str(days[month - 1])
        return self.get_metrics_day_to_day(col, start_t, end_t)


    def get_aver_day_to_day(self, col, start_t, end_t):
        all_metrics = self.get_metrics_day_to_day(col, start_t, end_t)
        aver_metrics = {}
        for metric in all_metrics:
            for key in metric:
                if key in aver_metrics.keys():
                    aver_metrics[key] += metric[key]
                else:
                    aver_metrics[key] = metric[key]
        for key in aver_metrics.keys():
            aver_metrics[key] /= len(aver_metrics)
        return aver_metrics


    def date_to_stamp(self, dt):
        if re.match(ur"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", dt):
            #time.strptime(dt, '%Y-%m-%d %H:%M:%S')
            s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
        elif re.match(ur"\d{4}-\d{2}-\d{2}", dt):
            dt += " 00:00:00"
            s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
        else:
            s = 0
        return int(s)
