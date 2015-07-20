from chris.generate_data import generate_cluster_data
from chris import clustering
import pprint

data = generate_cluster_data(5, 20)

fixed_data = zip(*data)

testdata = fixed_data[0]

for i in range(10):
    kmeans = clustering.KmeansCluster(testdata, 3, ['time'])
    kmeans.initialize()
    kmeans.cluster()

    for c in kmeans.clusters:
        print c.centroid
        pprint.pprint([item['time'] for item in c.points])
    print

    del kmeans
