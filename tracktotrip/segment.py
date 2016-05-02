from .Point import Point
from .smooth import smoothSegment
from .noiseDetection import removeNoise
from .simplify import simplify
from .preprocess import preprocessSegment
from .Location import inferLocation
from .transportationMode import inferTransportationMode

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def segmentSegment(points):
    """
    Makes spatiotemporal checks to see if two or more tracks are
    recorded in the current one

    Returns segmented
    """
    X = map(lambda p: p.gen3arr(), points)
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

class Segment:
    """Holds the points and semantic information about them

    Attributes:
        points: points of the segment
        transportationModes: array of transportation modes of the segment
            Each transportation mode represents a span of points
            Each span is a map in the following format:
                label: string with the type of transportation mode
                from: start of the span
                to: end of the span
        locationFrom: string with the semantic location of the start of the segment
        locationTo: string with the semantic location of the end of the segment
    """

    def __init__(self, points=[]):
        """Constructor

        Args:
            points: points of the segment
        """
        self.points = points
        self.transportationModes = []
        self.locationFrom = ""
        self.locationTo = ""

    def pointAt(self, i):
        """Point at index

        Args:
            i: index
        Returns:
            Point or index out of range exception
        """
        return self.points[i]

    def removeNoise(self, var=2):
        """In-place removal of noise points

        Applies removeNoise function to points

        Returns:
            This segment
        """
        self.points = removeNoise(self.points, var=2)
        return self

    def smooth(self):
        """In-place smoothing

        Applies smoothSegment function to points

        Returns:
            This segment
        """
        self.points = smoothSegment(self.points)
        return self

    def segment(self):
        """Spatio-temporal segmentation

        Applies segmentSegment function to points,
        without changing this segment

        Returns:
            An array of arrays of points
        """
        return segmentSegment(self.points)

    def simplify(self):
        """In-place segment simplification

        Applies simplify function to points

        Returns:
            This segment
        """
        self.points = simplify(self.points, 0.01, 5)
        return self

    def preprocess(self):
        """In-place segment preprocessing

        Applies preprocessSegment function to points

        Returns:
            This segment
        """
        points, skipped = preprocessSegment(self.points)
        self.points = points
        return self

    def inferLocation(self):
        """In-place location inferring

        Applies inferLocation function to points

        Returns:
            This segment
        """

        locations = inferLocation(self.points)
        self.locationFrom = locations[0]
        self.locationTo = locations[1]

        return self

    def inferTransportationMode(self):
        """In-place transportation mode inferring

        Applies inferTransportationMode function to points

        Returns:
            This segment
        """
        self.transportationModes = inferTransportationMode(self.points)
        return self

    def toJSON(self):
        """Converts segment to a JSON serializable format

        Returns:
            Map with the points, transportationModes and locations (from
                and to)and segments of the segment.
        """
        return {
                'points': map(lambda point: point.toJSON(), self.points),
                'transportationModes': self.transportationModes,
                'locationFrom': self.locationFrom,
                'locationTo': self.locationTo
                }

    def length(self):
        """Returns the number of point of the segment

        Returns:
            Number of points of the segment
        """
        return self.segments.length

    @staticmethod
    def fromGPX(gpxSegment):
        """Creates a Segment from a GPX format.

        No preprocessing is done.

        Arguments:
            gpxSegment: a gpxpy.GPXTrackSegment
        Return:
            A Segment instance
        """
        points = []
        for i, point in enumerate(gpxSegment.points):
            points.append(Point.fromGPX(point, i))
        return Segment(points)

    @staticmethod
    def fromJSON(json):
        """Creates a Segment from a JSON file.

        No preprocessing is done.

        Arguments:
            json: map with the keys: points, and optionally, transportationModes,
                locationFrom and locationTo.
        Return:
            A Segment instance
        """
        # FIXME
        points = []
        for i, point in enumerate(json['points']):
            points.append(Point.fromJSON(point, i))
        return Segment(points)

