import math
import datetime

epoch = datetime.datetime.utcfromtimestamp(0)

class Point:
    def __init__(self, index, lat, lon, time, dt=0, acc=0.0, vel=0.0):
        self.data = [index, lon, lat, time, dt, acc, vel]
    def getId(self):
        return self.data[0]
    def getLat(self):
        return self.data[2]
    def setLat(self, lat):
        self.data[2] = lat
    def getLon(self):
        return self.data[1]
    def setLon(self, lon):
        self.data[1] = lon
    def getTime(self):
        return self.data[3]
    def getDt(self):
        return self.data[4]
    def getAcc(self):
        return self.data[5]
    def getVel(self):
        return self.data[6]
    def getTimestamp(self):
        return ((self.getTime() - epoch).total_seconds() * 1000.0)
    def gen2arr(self):
        return [self.data[1], self.data[2]]
    def gen3arr(self):
        return [self.data[1], self.data[2], self.getTime()]
    # def __repr__(self):
        # return self.data.__repr__()
    @staticmethod
    def trackToArr2(track):
        return map(mapHelper, track)
    def distance(self, other):
        return distance(self.getLat(), self.getLon(), None, other.getLat(), other.getLon(), None)
    def timeDifference(self, previous):
        return abs(self.getTimestamp() - previous.getTimestamp())
    def computeMetrics(self, previous):
        dt = self.timeDifference(previous)
        vel = 0
        dv = 0
        acc = 0
        if dt != 0 :
            vel = self.distance(previous)/dt
            dv = vel - previous.getVel()
            acc = dv/dt

        self.data[5] = acc
        self.data[6] = vel

        return self

    @staticmethod
    def fromGPX(gpxTrackPoint, i=0):
        return Point(i, lat=gpxTrackPoint.latitude, lon=gpxTrackPoint.longitude, time=gpxTrackPoint.time)

    def toJSON(self):
        return {
                'lat': self.getLat(),
                'lon': self.getLon(),
                'time': self.getTime().isoformat()
                }

    @staticmethod
    def fromJSON(json, i=0):
        return Point(i, lat=json['lat'], lon=json['lon'], time=gt(json['time']))

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

