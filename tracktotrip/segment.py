import datetime
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

"""
Makes spatiotemporal checks to see if two or more tracks are
recorded in the current one

Returns segmented
"""
def segment(points):
    epoch = datetime.datetime.utcfromtimestamp(0)

    X = map(lambda p: [p.getLon(), p.getLat(), ((p.getTime() - epoch).total_seconds() * 1000.0)], points)
    X = StandardScaler().fit_transform(X)
    # eps=0.15,min_samples=80
    db = DBSCAN(eps=0.15, min_samples=80).fit(X)
    labels = db.labels_

    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    segments = [[] for o in range(n_clusters_+1)]
    clusters = [[] for o in range(n_clusters_+1)]
    currentSegment = 0
    for i, label in enumerate(labels):
        if label != -1 and label + 1 != currentSegment:
            currentSegment = label + 1
        point = points[i]
        segments[currentSegment].append(point)
        if label == -1:
            None
        else:
            clusters[label + 1].append(point)

    """print(map(lambda s: len(s), segments))
    for s in segments:
        print(str(s[0]) + str(s[-1]))"""

    p = [[] for o in range(n_clusters_)]
    for i, l in enumerate(labels):
        if l != -1:
            p[l].append(points[i])

    for i, w in enumerate(p):
        print("Cluster! " + str(i))
        print(w[0])
        print(w[-1])
        #centroid = Point(-1, np.mean(map(lambda p: p.getLon(), w)), np.mean(map(lambda p: p.getLat(), w)), w[-1].getTime())
        centroid = w[-1]
        #segments[i].append(centroid)

    print(len(segments))
    return segments
