#!/usr/bin/env python

import random
import math


class ClusterSet(object):

    def __init__(self, centroid, keys):
        self.centroid = {}
        for i in keys:
            self.centroid[i] = centroid[i]
            
        self.keys = keys
        self.points = []

    def recentroid(self):

        temp = {}
        for i in self.keys:
            temp[i] = 0.0

        for point in self.points:
            for i in self.keys:
                temp[i] += point[i]

        total = len(self.points)
        if total == 0:
            return False

        is_changed = False
        for i in self.keys:
            old = self.centroid[i]
            new = self.centroid[i] = temp[i]/total
            if abs(new - old) < 1e-12:
                is_changed |= False
            else:
                is_changed |= True

        return is_changed
	
    def merge(self, other):
        u = len(self.points)
        v = len(other.points)
        for i in self.keys:
            self.centroid[i] = (self.centroid[i]*u + other.centroid[i]*v)/(u+v)
        self.points += other.points
        
    def distance(self, other):
        dist = 0.0
        for i in self.keys:
            dist += (self.centroid[i] - other.centroid[i])**2
        return math.sqrt(dist)


    def clear(self):
        self.points = []

        
        
class KmeansCluster(object):
    
    def __init__(self, data, k, keys):
            
        self.k = k
        self.keys = keys
        self.data = data

    def initialize(self):
        self.clusters = []
        print "init : pick %d in %d"%(self.k, len(self.data))
        centroids = random.sample(self.data, self.k)
        for centroid in centroids:
            self.clusters.append(ClusterSet(centroid, self.keys))
        self.flag = True

    def cluster(self):
        while self.flag:

            for cluster in self.clusters:
                cluster.clear()

            for point in self.data:
                minimum = 100000000
                best = None
                for cluster in self.clusters:
                    d = 0.0
                    for i in self.keys:
                        d += (point[i] - cluster.centroid[i])**2
                    d = math.sqrt(d)
                    if d < minimum:
                        minimum = d
                        best = cluster

                best.points.append(point)

            is_changed = False
            for cluster in self.clusters:
                is_changed |= cluster.recentroid()

            self.flag &= is_changed



if __name__=="__main__":
    points = []
    
    for i in range(20):
        points.append({"x": random.uniform(9.5, 10.5), "y": random.randint(0, 1000)})
    for i in range(20):
        points.append({"x": random.uniform(49.5, 50.5), "y": random.randint(0, 1000)})      
    kmeans = KmeansCluster(points, 2, ['x'])
    kmeans.initialize()
    kmeans.cluster()
    for i in kmeans.clusters:
        print i.centroid
        print points
        print
