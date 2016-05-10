import math
import datetime

epoch = datetime.datetime.utcfromtimestamp(0)

class Point:
    """Point position representation

    Attributes:
        index: original index of point in segment
        lat: number, latitude
        lon: number, longitude
        time: datetime instance
        dt: time difference in seconds from the past point in the segment
            should be computed
        acc: float, accelaration in km^2/h, relative to the previous point in the segment
            should be computed with computeMetrics method
        vel: float, velocity in km/h, relative to the previous point in the segment
            should be computed with computeMetrics method
    """
    def __init__(self, index, lat, lon, time, dt=0, acc=0.0, vel=0.0):
        self.index = index
        self.lon = lon
        self.lat = lat
        self.time = time
        self.dt = dt
        self.acc = acc
        self.vel = vel

    def getTimestamp(self):
        """Gets the timestamp of this point's time,
        seconds since 1970

        Returns:
            Float
        """
        return (self.time - epoch).total_seconds()

    def gen2arr(self):
        """Generate a location array

        Returns:
            Array with longitude and latitude
        """
        return [self.lon, self.lat]

    def gen3arr(self):
        """Generate a time-location array

        Returns:
            Array with longitude, latitude and datetime instance
        """
        return [self.lon, self.lat, self.getTimestamp()]

    @staticmethod
    def trackToArr2(track):
        return map(mapHelper, track)

    def distance(self, other):
        """Distance between this and another Point

        Args:
            other: Point instance
        Returns:
            Distance, float, between the two points in km
        """
        return distance(self.lat, self.lon, None, other.lat, other.lon, None)

    def timeDifference(self, previous):
        """Calculates the time difference between two points

        Args:
            previous: Point instance
        Returns:
            Time difference, float, between the two points in seconds.
            May be positive if the other point occured before, negative
            otherwise.
        """
        return abs(self.getTimestamp() - previous.getTimestamp())

    def computeMetrics(self, previous):
        """Computes the metrics of this point

        Computes and updates the dt, vel and acc class attributes.

        Args:
            previous: Point instance, that occured before
        Returns:
            This Point instance
        """
        dt = self.timeDifference(previous)
        vel = 0
        dv = 0
        acc = 0
        if dt != 0 :
            vel = self.distance(previous)/dt
            dv = vel - previous.vel
            acc = dv/dt

        self.dt = dt
        self.acc = acc
        self.vel = vel
        return self

    @staticmethod
    def fromGPX(gpxTrackPoint, i=0):
        """Creates a Point from GPX representation

        Arguments:
            gpxTrackPoint: gpxpy.GPXTrackPoint instance
        Returns:
            Point instance
        """
        return Point(i, lat=gpxTrackPoint.latitude, lon=gpxTrackPoint.longitude, time=gpxTrackPoint.time)

    def toJSON(self):
        """Creates a JSON serializable representation of this Point

        Returns:
            Map with keys: lat, lon (both floats) and time (string, in ISO format)
        """
        return {
                'lat': self.lat,
                'lon': self.lon,
                'time': self.time.isoformat()
                }

    @staticmethod
    def fromJSON(json, i=0):
        """Creates Point instance from JSON representation

        Args:
            json: map representation of Point instance
        Returns:
            Point instance
        """
        return Point(i, lat=json['lat'], lon=json['lon'], time=gt(json['time']))

    @staticmethod
    def accessor(point):
        return point.lat, point.lon, point.time


ONE_DEGREE = 1000. * 10000.8 / 90.
EARTH_RADIUS = 6371 * 1000

def to_rad(x):
    return x / 180. * math.pi

def haversine_distance(latitude_1, longitude_1, latitude_2, longitude_2):
    """
    Haversine distance between two points, expressed in meters.
    Implemented from http://www.movable-type.co.uk/scripts/latlong.html
    """
    d_lat = to_rad(latitude_1 - latitude_2)
    d_lon = to_rad(longitude_1 - longitude_2)
    lat1 = to_rad(latitude_1)
    lat2 = to_rad(latitude_2)

    a = math.sin(d_lat/2) * math.sin(d_lat/2) + \
        math.sin(d_lon/2) * math.sin(d_lon/2) * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = EARTH_RADIUS * c

    return d

def distance(latitude_1, longitude_1, elevation_1, latitude_2, longitude_2, elevation_2,
             haversine=None):

    # If points too distant -- compute haversine distance:
    if haversine or (abs(latitude_1 - latitude_2) > .2 or abs(longitude_1 - longitude_2) > .2):
        return haversine_distance(latitude_1, longitude_1, latitude_2, longitude_2)

    coef = math.cos(latitude_1 / 180. * math.pi)
    x = latitude_1 - latitude_2
    y = (longitude_1 - longitude_2) * coef

    distance_2d = math.sqrt(x * x + y * y) * ONE_DEGREE

    if elevation_1 is None or elevation_2 is None or elevation_1 == elevation_2:
        return distance_2d

    return math.sqrt(distance_2d ** 2 + (elevation_1 - elevation_2) ** 2)

def mapHelper(p):
    if p == None:
        return None
    else:
        p.gen2arr()

def gt(dt_str):
    dt, _, us= dt_str.partition(".")
    dt= datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    us= int(us.rstrip("Z"), 10)
    return dt + datetime.timedelta(microseconds=us)

