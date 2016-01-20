import gpxpy
from .preprocess import preprocess as preprocess
import numpy as np
import matplotlib.pyplot as plt


def loadGPX(name):
    return gpxpy.parse(open(name, 'r'))

def trackFromGPX(name):
    return preprocess(loadGPX(name))

def trackToGPX(segments, filename):
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    for segment in segments:
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        for point in segment:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(point.getLat(), point.getLon(), time=point.getTime()))

    f = open(filename, 'w')
    f.write(gpx.to_xml())
    f.close()

def plotSegments(segments, line=False, annotate=False, xlim=None, ylim=None):
    plt.clf()
    if xlim!= None:
        plt.gca().set_xlim(xlim)
    if ylim!= None:
        plt.gca().set_ylim(ylim)

    colors = plt.cm.Spectral(np.linspace(0, 1, len(segments)))
    if line==True:
        for s, segment in enumerate(segments):
            plt.plot(map(lambda p: p.getLon(), segment), map(lambda p: p.getLat(), segment), 'bo-', color=colors[s])
    else:
        for s, segment in enumerate(segments):
            for i, point in enumerate(segment):
                y = point.getLat()
                x = point.getLon()
                if i==0:
                    plt.plot(x, y, 'o', markersize=12, markerfacecolor=colors[s])
                elif len(segment)-1 == i:
                    plt.plot(x, y, 'o', markersize=16, markerfacecolor=colors[s])
                else:
                    plt.plot(x, y, 'o', markersize=6, markerfacecolor=colors[s])
                if annotate:
                    plt.annotate(str(point.getId()) + " in " + str(i),
                            xy = (x, y), xytext = (-20, 20),
                            textcoords = 'offset points', ha = 'right', va = 'bottom',
                            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
    return plt
