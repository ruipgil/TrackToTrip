"""
Track class
"""
from copy import deepcopy
from os.path import basename

import gpxpy
import numpy as np
from rtree import index

from .segment import Segment
from .similarity import segment_similarity

DEFAULT_FILE_NAME_FORMAT = "%Y-%m-%d"

class Track(object):
    """Collection of segments

    This is a higher level class, all methods of TrackToTrip library
    can be called over this class

    Attributes:
        name: A string indicating the name of the track
        segments: Array of TrackToTrip Segments
        preprocessed: Boolean, true if it has been preprocessed
    """

    def __init__(self, name, segments):
        """ Constructor

        When constructing a track it's not guaranteed that the segments
        have their properties computed. Call preprocess method over this
        class, or over each segment to guarantee it.

        Args:
            name (:obj:`str`)
            segments(:obj:`list` of :obj:`Segment`)
        """
        self.name = name
        self.segments = sorted(segments, key=lambda s: s.points[0].time)
        self.preprocessed = False

    # def start_time(self):
    #     lastTime = None
    #     for segment in self.segments:
    #         if lastTime is None:
    #             lastTime = segment.getStartTime()
    #         elif lastTime > segment.getStartTime():
    #             lastTime = segment.getStartTime()
    #     return lastTime

    def generate_name(self, name_format=DEFAULT_FILE_NAME_FORMAT):
        """ Generates a name for the track

        The name is generated based on the date of the first point of the
        track, or in case it doesn't exist, "EmptyTrack"

        Args:
            name_format (str, optional): Name formar to give to the track, based on
                its start time. Defaults to DEFAULT_FILE_NAME_FORMAT
        Returns:
            str
        """
        if len(self.segments) > 0:
            return self.segments[0].points[0].time.strftime(name_format) + ".gpx"
        else:
            return "EmptyTrack"
    #
    # def remove_noise(self, var=2):
    #     """In-place removal of noise points
    #
    #     Arguments:
    #         var: Number to adjust noise removal sensitivity
    #     Returns:
    #         This track
    #     """
    #     for segment in self.segments:
    #         segment.removeNoise(var)
    #     return self

    def smooth(self, strategy, noise):
        """In-place smoothing of segments

        Returns:
            This track
        """
        for segment in self.segments:
            segment.smooth(strategy, noise)
        return self

    def segment(self, eps, min_time):
        """In-place segmentation of segments

        Spatio-temporal segmentation of each segment
        The number of segments may increse after this step

        Returns:
            This track
        """
        new_segments = []
        for segment in self.segments:
            segmented = segment.segment(eps, min_time)
            for seg in segmented:
                new_segments.append(Segment(seg))
        self.segments = new_segments
        return self

    def simplify(self, eps, dist_threshold, topology_only=False):
        """In-place simplification of segments

        Args:
            topology_only: Boolean, optional. True to keep
                the topology, neglecting velocity and time
                accuracy (use common Douglas-Ramen-Peucker).
                False (default) to simplify segments keeping
                the velocity between points.
        Returns:
            This track
        """
        for segment in self.segments:
            segment.simplify(eps, dist_threshold, topology_only)
        return self

    def infer_transportation_mode(self, clf, min_time):
        """In-place transportation mode inferring of segments

        Returns:
            This track
        """
        for segment in self.segments:
            segment.infer_transportation_mode(clf, min_time)
        return self

    def copy(self):
        """Creates a deep copy of itself

        All segments and points are copied

        Returns:
            A Track object different from this instance
        """
        return deepcopy(self)

    def to_trip(
            self,
            name,
            # noise_var=2,
            smooth_strategy,
            smooth_noise,
            seg_eps,
            seg_min_time,
            simplify_dist_threshold,
            # simplify_max_time=5,
            file_format
        ):
        """In-place, transformation of a track into a trip

        A trip is a more accurate depiction of reality than a
        track.
        For a track to become a trip it need to go through the
        following steps:
            + noise removal
            + smoothing
            + spatio-temporal segmentation
            + simplification
        At the end of these steps we have a less noisy, track
        that has less points, but that holds the same information.
        It's required that each segment has their metrics calculated
        or has been preprocessed.

        Args:
            name: An optional string with the name of the trip. If
                none is given, one will be generated by generateName
        Returns:
            This Track instance
        """
        if len(name) != 0:
            name = self.name
        else:
            name = self.generate_name(file_format)

        # self.removeNoise(noise_var)

        self.smooth(smooth_strategy, smooth_noise)

        self.compute_metrics()
        self.segment(seg_eps, seg_min_time)

        self.compute_metrics()
        self.simplify(None, simplify_dist_threshold)

        self.compute_metrics()
        self.name = name

        return self

    def preprocess(self, max_acc, destructive=True):
        """In-place preprocessing of segments

        Args:
            destructive: Optional, boolean. True to allow point
                removal. More details in preprocessSegment
        Returns:
            This track
        """
        self.segments = [segment.preprocess(max_acc, destructive) for segment in self.segments]
        self.preprocessed = True
        return self

    def infer_transportation_modes(self, dt_threshold=10):
        """In-place transportation inferring of segments

        Returns:
            This track
        """
        self.segments = [
            segment.infer_transportation_mode(dt_threshold=dt_threshold)
            for segment in self.segments
            ]
        return self

    # TODO
    def infer_location(
            self,
            location_query,
            max_distance,
            google_key,
            limit
        ):
        """In-place location inferring of segments

        Returns:
            This track
        """
        self.segments = [
            segment.infer_location(location_query, max_distance, google_key, limit)
            for segment in self.segments
            ]
        return self

    def to_json(self):
        """Converts track to a JSON serializable format

        Returns:
            Map with the name, and segments of the track.
        """
        return {
            'name': self.name,
            'segments': [segment.to_json() for segment in self.segments]
            }

    # TODO
    def merge_and_fit(self, track, pairings):
        """ Merges another track with this one, ordering the points based on a
            distance heuristic

        Args:
            track (:obj:`Track`): Track to merge with
            pairings
        Returns:
            :obj:`Segment`: self
        """
        for (self_seg_index, track_seg_index, _) in pairings:
            self_s = self.segments[self_seg_index]
            track_s = track.segments[track_seg_index]

            self_s.merge_and_fit(track_s)
        return self

    def get_point_index(self, point):
        """ Gets of the closest first point

        Args:
            point (:obj:`Point`)
        Returns:
            (int, int): Segment id and point index in that segment
        """
        for i, segment in enumerate(self.segments):
            idx = segment.getPointIndex(point)
            if idx != -1:
                return i, idx
        return -1, -1

    def bounds(self):
        """ Gets the bounds of this segment

        Returns:
            (float, float, float, float): Bounds, with min latitude, min longitude,
                max latitude and max longitude
        """
        min_lat = float("inf")
        min_lon = float("inf")
        max_lat = -float("inf")
        max_lon = -float("inf")
        for segment in self.segments:
            milat, milon, malat, malon = segment.getBounds()
            min_lat = min(milat, min_lat)
            min_lon = min(milon, min_lon)
            max_lat = max(malat, max_lat)
            max_lon = max(malon, max_lon)
        return min_lat, min_lon, max_lat, max_lon

    def has_point(self, point):
        """ Checks if a point exist in any of the segments

        Args:
            points (:obj:`Point`)
        Returns:
            bool
        """
        s_ix, _ = self.get_point_index(point)
        return s_ix != -1

    def similarity(self, track):
        """ Compares two tracks based on their topology

        This method compares the given track against this
        instance. It only verifies if given track is close
        to this one, not the other way arround

        Args:
            track (:obj:`Track`)
        Returns:
            Two-tuple with global similarity between tracks
            and an array the similarity between segments
        """
        idx = index.Index()
        i = 0
        for i, segment in enumerate(self.segments):
            idx.insert(i, segment.bounds(), obj=segment)

        final_siml = []
        final_diff = []
        for i, segment in enumerate(track.segments):
            query = idx.intersection(segment.bounds(), objects=True)

            res_siml = []
            res_diff = []
            for result in query:
                siml, diff = segment_similarity(segment, result.object)
                res_siml.append(siml)
                res_diff.append((result.id, i, diff))
                # print(result.id, i, diff)

            # print("seg match", res_siml, res_diff)

            if len(res_siml) > 0:
                final_siml.append(max(res_siml))
                final_diff.append(res_diff[np.argmax(res_siml)])
            else:
                final_siml.append(0)
                final_diff.append([])

        return np.mean(final_siml), final_diff

    def compute_metrics(self):
        """ Computes metrics for every segment's point

        See Segment.compute_metrics

        Returns:
            :obj:`Track`: Self
        """
        for segment in self.segments:
            segment.compute_metrics()
        return self

    def to_gpx(self):
        """Converts track to a GPX format

        Uses GPXPY library as an intermediate format

        Returns:
            A string with the GPX/XML track
        """
        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        for segment in self.segments:
            gpx_segment = gpxpy.gpx.GPXTrackSegment()
            gpx_track.segments.append(gpx_segment)

            for point in segment.points:
                gpx_point = gpxpy.gpx.GPXTrackPoint(point.lat, point.lon, time=point.time)
                gpx_segment.points.append(gpx_point)
        return gpx.to_xml()

    def to_life(self):
        """Converts track to LIFE format
        """
        buff = "--%s\n" % self.segments[0].points[0].time.strftime("%Y_%m_%d")
        # buff += "--" + day
        # buff += "UTC+s" # if needed

        def military_time(time):
            """ Converts time to military time

            Args:
                time (:obj:`datetime.datetime`)
            Returns:
                str: Time in the format 1245 (12 hours and 45 minutes)
            """
            return time.strftime("%H%M")

        def stay(buff, start, end, place):
            """ Creates a stay representation

            Args:
                start (:obj:`datetime.datetime` or str)
                end (:obj:`datetime.datetime` or str)
                place (:obj:`Location`)
            Returns:
                str
            """
            if not isinstance(start, str):
                start = military_time(start)
            if not isinstance(end, str):
                end = military_time(end)

            return "%s\n%s-%s: %s" % (buff, start, end, place.label)

        def trip(buff, segment):
            """ Creates a trip representation

            Args:
                buff (str): buffer
                segment (:obj:`Segment`)
            Returns:
                str: buffer and trip representation
            """
            trip = "%s-%s: %s -> %s" % (
                military_time(segment.points[0].time),
                military_time(segment.points[-1].time),
                segment.location_from.label,
                segment.location_to.label
            )

            t_modes = segment.transportation_modes
            if len(t_modes) == 1:
                trip = "%s [%s]" % (trip, t_modes[0]['label'])
            else:
                modes = []
                for mode in t_modes:
                    trip_from = military_time(segment.points[mode['from']].time)
                    trip_to = military_time(segment.points[mode['to']].time)
                    modes.append("    %s-%s: [%s]" % (trip_from, trip_to, mode['label']))
                trip = "%s\n%s" % (trip, "\n".join(modes))

            return "%s\n%s" % (buff, trip)

        last = len(self.segments) - 1
        for i, segment in enumerate(self.segments):
            if i == 0:
                buff = stay(
                    buff,
                    "0000",
                    military_time(segment.points[0].time),
                    segment.location_from
                )
            buff = trip(buff, segment)
            if i is last:
                buff = stay(
                    buff,
                    military_time(segment.points[0].time),
                    "2359",
                    segment.location_to
                )
            else:
                next_seg = self.segments[i+1]
                buff = stay(
                    buff,
                    military_time(segment.points[-1].time),
                    military_time(next_seg.points[0].time),
                    segment.location_from
                )

        return buff

    @staticmethod
    def from_gpx(file_path):
        """ Creates a Track from a GPX file.

        No preprocessing is done.

        Arguments:
            file_path (str): file path and name to the GPX file
        Return:
            :obj:`list` of :obj:`Track`
        """
        gpx = gpxpy.parse(open(file_path, 'r'))
        file_name = basename(file_path)

        tracks = []
        for i, track in enumerate(gpx.tracks):
            segments = []
            for segment in track.segments:
                segments.append(Segment.from_gpx(segment))

            if len(gpx.tracks) > 1:
                name = file_name + "_" + str(i)
            else:
                name = file_name
            tracks.append(Track(name, segments))

        return tracks

    @staticmethod
    def from_json(json):
        """Creates a Track from a JSON file.

        No preprocessing is done.

        Arguments:
            json: map with the keys: name (optional) and segments.
        Return:
            A track instance
        """
        segments = [Segment.from_json(s) for s in json['segments']]
        return Track(json['name'], segments).compute_metrics()
