from .Point import Point
from smooth import smooth_segment
from .noiseDetection import removeNoise
from .simplify import simplify
from .preprocess import preprocessSegment
from .Location import inferLocation
from .transportationMode import inferTransportationMode
from .spatiotemporal_segmentation import spatiotemporal_segmentation
from .drp import drp
from .similarity import sortSegmentPoints

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
        locationFrom: TrackToTrip.Location or None, the semantic location of
            the start of the segment
        locationTo: TrackToTrip.Location or None, the semantic location of
            the end of the segment
    """

    def __init__(self, points=[]):
        """Constructor

        Args:
            points: points of the segment
        """
        self.points = points
        self.transportation_modes = []
        self.location_from = None
        self.location_to = None

    def pointAt(self, i):
        """Point at index

        Args:
            i: index
        Returns:
            Point or index out of range exception
        """
        return self.points[i]

    def getStartTime(self):
        return self.points[0].time

    def getEndTime(self):
        return self.points[-1].time

    def getBounds(self, lowerIndex = 0, upperIndex = -1):
        """Computes the bounds of the segment, or part of it

        Args:
            lowerIndex: Optional, start index. Default is 0
            upperIndex: Optional, end index. Default is -1,
                the last point
        Returns:
            Array with two arrays. The first one with the
            minimum latitude and longitude, the second with
            the maximum latitude and longitude of the segment
            slice
        """
        pointSet = self.points[lowerIndex:upperIndex]

        minLat = float("inf")
        minLon = float("inf")
        maxLat = -float("inf")
        maxLon = -float("inf")

        for point in pointSet:
            minLat = min(minLat, point.lat)
            minLon = min(minLon, point.lon)
            maxLat = max(maxLat, point.lat)
            maxLon = max(maxLon, point.lon)

        return (minLat, minLon, maxLat, maxLon)


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
        self.points = smooth_segment(self.points)
        return self

    def segment(self):
        """Spatio-temporal segmentation

        Applies segmentSegment function to points,
        without changing this segment

        Returns:
            An array of arrays of points
        """
        return spatiotemporal_segmentation(self.points)

    def simplify(self, topology_only=False):
        """In-place segment simplification

        Applies simplify function to points

        Args:
            topology_only: Boolean, optional. True to keep
                the topology, neglecting velocity and time
                accuracy (use common Douglas-Ramen-Peucker).
                False (default) to simplify segment keeping
                the velocity between points.
        Returns:
            This segment
        """
        if topology_only:
            self.points = drp(self.points, 0.0001)
        else:
            self.points = simplify(self.points, 0.01, 5)
        return self

    def preprocess(self, destructive=True):
        """In-place segment preprocessing

        Applies preprocessSegment function to points

        Args:
            destructive: Optional, boolean. True to allow point
                removal. More details in preprocessSegment
        Returns:
            This segment
        """
        points, skipped = preprocessSegment(self.points, destructive=destructive)
        self.points = points
        return self

    def inferLocation(self):
        """In-place location inferring

        Applies inferLocation function to points

        Returns:
            This segment
        """

        locations = inferLocation(self.points)
        self.location_from = locations[0]
        self.location_to = locations[1]

        return self

    def inferTransportationMode(self):
        """In-place transportation mode inferring

        Applies inferTransportationMode function to points

        Returns:
            This segment
        """
        self.transportation_modes = inferTransportationMode(self.points)
        return self

    def merge_and_fit(self, segment):
        """Merge points with another segment points

        """
        self.points = sortSegmentPoints(self.points, segment.points)
        return self

    def toJSON(self):
        """Converts segment to a JSON serializable format

        Returns:
            Map with the points, transportationModes and locations (from
                and to)and segments of the segment.
        """
        return {
                'points': map(lambda point: point.toJSON(), self.points),
                'transportationModes': self.transportation_modes,
                'locationFrom': self.location_from.toJSON() if self.location_from != None else None,
                'locationTo': self.location_to.toJSON() if self.location_to != None else None
                }

    def length(self):
        """Returns the number of point of the segment

        Returns:
            Number of points of the segment
        """
        return len(self.points)

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

