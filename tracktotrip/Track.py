import gpxpy
from os.path import basename
import matplotlib.pyplot as plt
from .segment import Segment

DEFAULT_FILE_NAME_FORMAT = "%Y-%m-%d"

class Track:
    def __init__(self, name="", segments=[]):
        self.name = name
        self.segments = segments
        self.locations = []

    def segmentAt(self, i):
        return self.segments[i]

    def generateName(self):
        if len(self.segments) > 0:
            return self.segmentAt(0).pointAt(0).getTime().strftime(DEFAULT_FILE_NAME_FORMAT) + ".gpx"
        else:
            return "EmptyTrack"

    def removeNoise(self, var=2):
        for segment in self.segments:
            segment.removeNoise(var)
        return self

    def smooth(self):
        for segment in self.segments:
            segment.smooth()
        return self

    def segment(self):
        newSegments = []
        for segment in self.segments:
            s = segment.segment()
            for a in s:
                newSegments.append(Segment(a))
        self.segments = newSegments
        return self

    def simplify(self):
        for segment in self.segments:
            segment.simplify()
        return self

    def inferTransportationMode(self):
        for segment in self.segments:
            segment.inferTransportationMode()
        return self

    def copy(self):
        return self

    def toTrip(self, name=""):
        if len(name) != 0:
            name = self.name
        else:
            name = self.generateName()

        self.removeNoise(2)
        self.smooth()
        self.segment()
        for segment in self.segments:
            plt.plot(map(lambda p: p.getVel(), segment.points))
        plt.savefig("a.png", dpi=200, format='png', transparent=True, figsize=(10, 10))
        # self.simplify()
        self.name = name

        return self

    def preprocess(self):
        self.segments = map(lambda segment: segment.preprocess(), self.segments)
        return self

    def inferTransportationModes(self):
        self.segments = map(lambda segment: segment.inferTransportationMode(), self.segments)
        return self

    def inferLocation(self):
        self.locations = map(lambda segment: segment.inferLocation(), self.segments)
        return self

    def toJSON(self):
        return {
                'name': self.name,
                'segments': map(lambda segment: segment.toJSON(), self.segments),
                'locations': map(lambda location: [location[0].toJSON(), location[1].toJSON()], self.locations)
                }

    def toGPX():
        print("toImplement")

    @staticmethod
    def fromGPX(filePath):
        gpx = gpxpy.parse(open(filePath, 'r'))
        fileName = basename(filePath)

        tracks = []
        for ti, track in enumerate(gpx.tracks):
            segments = []
            for segment in track.segments:
                segments.append(Segment.fromGPX(segment))

            if len(gpx.tracks) > 1:
                name = fileName + "_" + str(ti)
            else:
                name = fileName
            tracks.append(Track(name, segments))

        return tracks

    @staticmethod
    def fromJSON(json):
        segments = map(lambda s: Segment.fromJSON(s), json['segments'])
        return Track(json['name'], segments).preprocess()

