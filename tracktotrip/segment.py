"""
Point segment module
"""
from copy import deepcopy
import sys
import traceback

import numpy as np

from .point import Point
from .utils import pairwise
from .smooth import with_extrapolation, with_inverse, INVERSE_STRATEGY, EXTRAPOLATE_STRATEGY
from .location import infer_location
from .similarity import sort_segment_points
from .compression import spt, drp
from .transportation_mode import speed_clustering
from .spatiotemporal_segmentation import spatiotemporal_segmentation

def remove_liers(points):
    """ Removes obvious noise points

    Checks time consistency, removing points that appear out of order

    Args:
        points (:obj:`list` of :obj:`Point`)
    Returns:
        :obj:`list` of :obj:`Point`
    """
    result = [points[0]]
    for i in range(1, len(points) - 2):
        prv = points[i-1]
        crr = points[i]
        nxt = points[i+1]
        if prv.time <= crr.time and crr.time <= nxt.time:
            result.append(crr)
    result.append(points[-1])

    return result

class Segment(object):
    """Holds the points and semantic information about them

    Attributes:
        points (:obj:`list` of :obj:`Point`): points of the segment
        #TODO
        transportation_modes: array of transportation modes of the segment
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

    def __init__(self, points):
        self.points = points
        self.transportation_modes = []
        self.location_from = None
        self.location_to = None

    def bounds(self, lower_index=0, upper_index=-1):
        """ Computes the bounds of the segment, or part of it

        Args:
            lower_index (int, optional): Start index. Defaults to 0
            upper_index (int, optional): End index. Defaults to 0
        Returns:
            :obj:`tuple` of :obj:`float`: Bounds of the (sub)segment, such that
                (min_lat, min_lon, max_lat, max_lon)
        """
        points = self.points[lower_index:upper_index]

        min_lat = float("inf")
        min_lon = float("inf")
        max_lat = -float("inf")
        max_lon = -float("inf")

        for point in points:
            min_lat = min(min_lat, point.lat)
            min_lon = min(min_lon, point.lon)
            max_lat = max(max_lat, point.lat)
            max_lon = max(max_lon, point.lon)

        return (min_lat, min_lon, max_lat, max_lon)

    def remove_noise(self):
        """In-place removal of noise points

        See `remove_noise` function

        Returns:
            :obj:`Segment`
        """
        self.points = remove_liers(self.points)
        return self

    def smooth(self, noise, strategy=INVERSE_STRATEGY):
        """ In-place smoothing

        See smooth_segment function

        Args:
            noise (float): Noise expected
            strategy (int): Strategy to use. Either smooth.INVERSE_STRATEGY
                or smooth.EXTRAPOLATE_STRATEGY
        Returns:
            :obj:`Segment`
        """
        if strategy is INVERSE_STRATEGY:
            self.points = with_inverse(self.points, noise)
        elif strategy is EXTRAPOLATE_STRATEGY:
            self.points = with_extrapolation(self.points, noise, 30)
        return self

    def segment(self, eps, min_time):
        """Spatio-temporal segmentation

        See spatiotemporal_segmentation function

        Args:
            eps (float): Maximum distance between two samples
            min_time (float): Minimum time between to segment
        Returns:
            :obj:`list` of :obj:`Point`
        """
        return spatiotemporal_segmentation(self.points, eps, min_time)

    def simplify(self, eps, max_dist_error, max_speed_error, topology_only=False):
        """ In-place segment simplification

        See `drp` and `compression` modules

        Args:
            eps (float): Distance threshold for the `drp` function
            max_dist_error (float): Max distance error, in meters
            max_speed_error (float): Max speed error, in km/h
            topology_only (bool, optional): True to only keep topology, not considering
                times when simplifying. Defaults to False.
        Returns:
            :obj:`Segment`
        """
        if topology_only:
            self.points = drp(self.points, eps)
        else:
            self.points = spt(self.points, max_dist_error, max_speed_error)
        return self

    def compute_metrics(self):
        """ Computes metrics for each point

        Returns:
            :obj:`Segment`: self
        """
        for prev, point in pairwise(self.points):
            point.compute_metrics(prev)
        return self

    def infer_location(
            self,
            location_query,
            max_distance,
            google_key,
            foursquare_client_id,
            foursquare_client_secret,
            limit
        ):
        """In-place location inferring

        See infer_location function

        Args:
        Returns:
            :obj:`Segment`: self
        """

        self.location_from = infer_location(
            self.points[0],
            location_query,
            max_distance,
            google_key,
            foursquare_client_id,
            foursquare_client_secret,
            limit
        )
        self.location_to = infer_location(
            self.points[-1],
            location_query,
            max_distance,
            google_key,
            foursquare_client_id,
            foursquare_client_secret,
            limit
        )

        return self

    def infer_transportation_mode(self, clf, min_time):
        """In-place transportation mode inferring

        See infer_transportation_mode function

        Args:
        Returns:
            :obj:`Segment`: self
        """
        self.transportation_modes = speed_clustering(clf, self.points, min_time)
        return self

    def merge_and_fit(self, segment):
        """ Merges another segment with this one, ordering the points based on a
            distance heuristic

        Args:
            segment (:obj:`Segment`): Segment to merge with
        Returns:
            :obj:`Segment`: self
        """
        self.points = sort_segment_points(self.points, segment.points)
        return self

    def closest_point_to(self, point, thr=20.0):
        """ Finds the closest point in the segment to a given point

        Args:
            point (:obj:`Point`)
            thr (float, optional): Distance threshold, in meters, to be considered
                the same point. Defaults to 20.0
        Returns:
            int: Index of the point. -1 if doesn't exist
        """
        distances = [p.distance(point) for p in self.points]
        min_index = np.argmin(distances)

        if distances[min_index] > thr:
            return -1
        else:
            return min_index

    def slice(self, start, end):
        """ Creates a copy of the current segment between indexes. If end > start,
            points are reverted

        Args:
            start (int): Start index
            end (int): End index
        Returns:
            :obj:`Segment`
        """

        reverse = False
        if start > end:
            temp = start
            start = end
            end = temp
            reverse = True

        seg = self.copy()
        seg.points = seg.points[start:end+1]
        if reverse:
            seg.points = list(reversed(seg.points))

        return seg

    def copy(self):
        """ Creates a deep copy of this instance

        Returns:
            :obj:`Segment`
        """
        return deepcopy(self)

    def to_json(self):
        """ Converts segment to a JSON serializable format

        Returns:
            :obj:`dict`
        """
        points = [point.to_json() for point in self.points]
        return {
            'points': points,
            'transportationModes': self.transportation_modes,
            'locationFrom': self.location_from.to_json() if self.location_from != None else None,
            'locationTo': self.location_to.to_json() if self.location_to != None else None
        }

    @staticmethod
    def from_gpx(gpx_segment):
        """ Creates a segment from a GPX format.

        No preprocessing is done.

        Arguments:
            gpx_segment (:obj:`gpxpy.GPXTrackSegment`)
        Return:
            :obj:`Segment`
        """
        points = []
        for point in gpx_segment.points:
            points.append(Point.from_gpx(point))
        return Segment(points)

    @staticmethod
    def from_json(json):
        """ Creates a segment from a JSON file.

        No preprocessing is done.

        Arguments:
            json (:obj:`dict`): JSON representation. See to_json.
        Return:
            :obj:`Segment`
        """
        points = []
        for point in json['points']:
            points.append(Point.from_json(point))
        return Segment(points)
