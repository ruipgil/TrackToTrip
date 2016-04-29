from .Point import Point
from .smooth import smoothSegment
from .noiseDetection import removeNoise
from .simplify import simplify
from .preprocess import preprocessSegment
from .Location import inferLocation
from .transportationMode import inferTransportationMode

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

"""
Makes spatiotemporal checks to see if two or more tracks are
recorded in the current one

Returns segmented
"""
def segmentSegment(points):
    X = map(lambda p: [p.getLon(), p.getLat(), p.getTimestamp()], points)
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

    for si, segment in enumerate(segments):
        if (len(segments) - 1) > si:
            print(len(segments), si)
            print(segments[si + 1][0].toJSON())
            #segment.append(segments[si + 1][0])

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

class Segment:
    def __init__(self, points=[]):
        self.points = points
        self.transportationModes = []

    def pointAt(self, i):
        return self.points[i]

    def removeNoise(self, var=2):
        self.points = removeNoise(self.points, var=2)
        return self

    def smooth(self):
        self.points = smoothSegment(self.points)
        return self

    def segment(self):
        return segmentSegment(self.points)

    def simplify(self):
        self.points = simplify(self.points, 0.01, 5)
        return self

    def preprocess(self):
        points, skipped = preprocessSegment(self.points)
        self.points = points
        return self

    def inferLocation(self):
        return inferLocation(self.points)

    def inferTransportationMode(self):
        self.transportationModes = inferTransportationMode(self.points)
        return self

    def toJSON(self):
        print(self.transportationModes)
        return {
                'points': map(lambda point: point.toJSON(), self.points),
                'transportationModes': self.transportationModes
                }

    def length(self):
        return self.segments.length

    @staticmethod
    def fromGPX(gpxSegment):
        points = []
        for i, point in enumerate(gpxSegment.points):
            points.append(Point.fromGPX(point, i))
        return Segment(points)

    @staticmethod
    def fromJSON(json):
        points = []
        for i, point in enumerate(json['points']):
            points.append(Point.fromJSON(point, i))
        return Segment(points)
