"""
Point class
"""
import math
import datetime
from .utils import isostr_to_datetime

EPOCH = datetime.datetime.utcfromtimestamp(0)

class Point(object):
    """ Spaciotemporal point representation

    Attributes:
        lat (float): latitude
        lon (float): longitude
        time (:obj:`datetime.datetime`): time
        dt (float): time difference in seconds from the past point in the segment
            should be computed
        acc (float): accelaration in km^2/h, relative to the previous point in the segment
            should be computed with compute_metrics method
        vel (float): velocity in km/h, relative to the previous point in the segment
            should be computed with compute_metrics method
    """
    def __init__(self, lat, lon, time):
        self.lon = lon
        self.lat = lat
        self.time = time
        self.dt = .0 #pylint: disable=invalid-name
        self.acc = .0
        self.vel = .0

    def get_timestamp(self):
        """ Gets the timestamp of this point's time, seconds since 1970

        Returns:
            float: time since epoch, in seconds
        """
        return (self.time - EPOCH).total_seconds()

    def gen2arr(self):
        """ Generate a location array

        Returns:
            :obj:`list` of float: List with longitude and latitude
        """
        return [self.lon, self.lat]

    def gen3arr(self):
        """ Generate a time-location array

        Returns:
            :obj:`list` of float: List with longitude, latitude and timestamp
        """
        return [self.lon, self.lat, self.get_timestamp()]

    def distance(self, other):
        """ Distance between points

        Args:
            other (:obj:`Point`)
        Returns:
            float: Distance in km
        """
        return distance(self.lat, self.lon, None, other.lat, other.lon, None)

    def time_difference(self, previous):
        """ Calcultes the time difference against another point

        Args:
            previous (:obj:`Point`): Point before
        Returns:
            Time difference in seconds
        """
        return abs((self.time - previous.time).total_seconds())

    def compute_metrics(self, previous):
        """ Computes the metrics of this point

        Computes and updates the dt, vel and acc attributes.

        Args:
            previous (:obj:`Point`): Point before
        Returns:
            :obj:`Point`: Self
        """
        delta_t = self.time_difference(previous)
        vel = 0
        delta_v = 0
        acc = 0
        if delta_t != 0:
            vel = self.distance(previous)/delta_t
            delta_v = vel - previous.vel
            acc = delta_v/delta_t

        self.dt = delta_t
        self.acc = acc
        self.vel = vel
        return self

    @staticmethod
    def from_gpx(gpx_track_point):
        """ Creates a point from GPX representation

        Arguments:
            gpx_track_point (:obj:`gpxpy.GPXTrackPoint`)
        Returns:
            :obj:`Point`
        """
        return Point(
            lat=gpx_track_point.latitude,
            lon=gpx_track_point.longitude,
            time=gpx_track_point.time
        )

    def to_json(self):
        """ Creates a JSON serializable representation of this instance

        Returns:
            :obj:`dict`: For example,
                {
                    "lat": 9.3470298,
                    "lon": 3.79274,
                    "time": "2016-07-15T15:27:53.574110"
                }
        """
        return {
            'lat': self.lat,
            'lon': self.lon,
            'time': self.time.isoformat()
        }

    @staticmethod
    def from_json(json):
        """ Creates Point instance from JSON representation

        Args:
            json (:obj:`dict`): Must have at least the following keys: lat (float), lon (float),
                time (string in iso format). Example,
                {
                    "lat": 9.3470298,
                    "lon": 3.79274,
                    "time": "2016-07-15T15:27:53.574110"
                }
            json: map representation of Point instance
        Returns:
            :obj:`Point`
        """
        return Point(
            lat=json['lat'],
            lon=json['lon'],
            time=isostr_to_datetime(json['time'])
        )


ONE_DEGREE = 1000. * 10000.8 / 90.
EARTH_RADIUS = 6371 * 1000

def to_rad(number):
    """ Degrees to rads """
    return number / 180. * math.pi

def haversine_distance(latitude_1, longitude_1, latitude_2, longitude_2):
    """
    Haversine distance between two points, expressed in meters.
    Implemented from http://www.movable-type.co.uk/scripts/latlong.html
    """
    d_lat = to_rad(latitude_1 - latitude_2)
    d_lon = to_rad(longitude_1 - longitude_2)
    lat1 = to_rad(latitude_1)
    lat2 = to_rad(latitude_2)

    #pylint: disable=invalid-name
    a = math.sin(d_lat/2) * math.sin(d_lat/2) + \
        math.sin(d_lon/2) * math.sin(d_lon/2) * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = EARTH_RADIUS * c

    return d

#pylint: disable=too-many-arguments
def distance(latitude_1, longitude_1, elevation_1, latitude_2, longitude_2, elevation_2,
             haversine=None):
    """ Distance between two points """

    # If points too distant -- compute haversine distance:
    if haversine or (abs(latitude_1 - latitude_2) > .2 or abs(longitude_1 - longitude_2) > .2):
        return haversine_distance(latitude_1, longitude_1, latitude_2, longitude_2)

    coef = math.cos(latitude_1 / 180. * math.pi)
    #pylint: disable=invalid-name
    x = latitude_1 - latitude_2
    y = (longitude_1 - longitude_2) * coef

    distance_2d = math.sqrt(x * x + y * y) * ONE_DEGREE

    if elevation_1 is None or elevation_2 is None or elevation_1 == elevation_2:
        return distance_2d

    return math.sqrt(distance_2d ** 2 + (elevation_1 - elevation_2) ** 2)
