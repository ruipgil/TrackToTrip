from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def spatiotemporal_segmentation(points, eps=0.15, min_samples=80):
    """
    Makes spatiotemporal checks to see if two or more tracks are
    recorded in the current one

    Returns segmented
    """
    X = map(lambda p: p.gen3arr(), points)
    X = StandardScaler().fit_transform(X)
    # eps=0.15,min_samples=80
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
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

    # for si, segment in enumerate(segments):
        # if (len(segments) - 1) > si:
            # print(len(segments), si)
            # print(segments[si + 1][0].toJSON())
            # #segment.append(segments[si + 1][0])

    """print(map(lambda s: len(s), segments))
    for s in segments:
        print(str(s[0]) + str(s[-1]))"""

    p = [[] for o in range(n_clusters_)]
    for i, l in enumerate(labels):
        if l != -1:
            p[l].append(points[i])

    # for i, w in enumerate(p):
        # print("Cluster! " + str(i))
        # print(w[0])
        # print(w[-1])
        # #centroid = Point(-1, np.mean(map(lambda p: p.getLon(), w)), np.mean(map(lambda p: p.getLat(), w)), w[-1].getTime())
        # centroid = w[-1]
        # #segments[i].append(centroid)

    # print(len(segments))
    return segments

