import sys
import gpxpy
import gpxpy.gpx
import datetime
#import time
import numpy as np
from sklearn.cluster import DBSCAN
from pykalman import KalmanFilter
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import copy

def loadFile(name):
    return gpxpy.parse(open(name, 'r'))

MAX_ACC = 10.2
"""
Pre-processing of gpx file.
Removes epoch points
Calculates speed and acceleration
Removes points that have an acceleration >2Gs

Returns an array of points
"""
def preprocess(gpx):
    result = []
    lastPoint = None
    lastGpxPoint = None
    cc = 0
    for ti, track in enumerate(gpx.tracks):
        for si, segment in enumerate(track.segments):
            for pi, point in enumerate(segment.points):
                if not shouldRemoveEpoch(point):
                    if lastPoint == None:
                        thisPoint = createPointFromGPX(pi, point)
                    else:
                        thisPoint = createPointFromGPXs(pi, point, lastGpxPoint, lastPoint)
                    if abs(thisPoint.getAcc()) <= MAX_ACC:
                        if pi >= 180 and pi <= 190:
                            print("[" + str(pi) + "]\tPoint:    " + str(thisPoint) + "\n\tPrevious: " + str(lastPoint))
                        result.append(thisPoint)
                        lastPoint = thisPoint
                        lastGpxPoint = point

                    else:
                        thisPoint = Point(pi, lastGpxPoint.latitude, lastGpxPoint.longitude, point.time, point.time_difference(lastGpxPoint))
                        if pi >= 180 and pi <= 190:
                            print("[" + str(pi) + "]\tPoint:    " + str(thisPoint) + "\n\tPrevious: " + str(lastPoint))
                        result.append(thisPoint)
                        lastPoint = thisPoint
                        temp = copy.deepcopy(point)
                        temp.latitude = lastGpxPoint.latitude
                        temp.longitude = lastGpxPoint.longitude
                        lastGpxPoint = temp
                        #print("dropped " + str(thisPoint))
                        cc = cc + 1
    print("acc removed " + str(cc))
    return result

def shouldRemoveEpoch(gpxPoint):
    return gpxPoint.time < datetime.datetime(1999, 1, 1)

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
    def gen2arr(self):
        return [self.data[1], self.data[2]]
    def gen3arr(self):
        return [self.data[1], self.data[2], self.getTime()]
    def __repr__(self):
        return self.data.__repr__()

def createPointFromGPX(i, point):
    return Point(i, point.latitude, point.longitude, point.time)

def createPointFromGPXs(i, point, previousGpx, previous):
    dt = point.time_difference(previousGpx)
    vel = point.distance_2d(previousGpx)/dt
    dv = vel - previous.getVel()
    acc = dv/dt
    return Point(i, point.latitude, point.longitude, point.time, dt, acc, vel)


"""
Makes spatiotemporal checks to see if two or more tracks are
recorded in the current one

Returns segmented
"""
def segment(points):
    epoch = datetime.datetime.utcfromtimestamp(0)

    X = map(lambda p: [p.getLon(), p.getLat(), ((p.getTime() - epoch).total_seconds() * 1000.0)], points)
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

    """print(map(lambda s: len(s), segments))
    for s in segments:
        print(str(s[0]) + str(s[-1]))"""

    p = [[] for o in range(n_clusters_)]
    for i, l in enumerate(labels):
        if l != -1:
            p[l].append(points[i])

    for i, w in enumerate(p):
        print("Cluster! " + str(i))
        print(w[0])
        print(w[-1])
        #centroid = Point(-1, np.mean(map(lambda p: p.getLon(), w)), np.mean(map(lambda p: p.getLat(), w)), w[-1].getTime())
        centroid = w[-1]
        #segments[i].append(centroid)

    print(len(segments))
    return segments

def plotSegments(segments, annotate=True):
    colors = plt.cm.Spectral(np.linspace(0, 1, len(segments)))
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
    plt.show()

def presmooth(points):
    points = points[:]
    inners = []
    lat = []
    lon = []
    last = None
    for point in points:
        if last!=None:
            inners.append(np.inner(point.getLat(), point.getLon()))
            lat.append(last.getLat()-point.getLat())
            lon.append(last.getLon()-point.getLon())
        last = point

    angle = np.mean(inners)
    dts = np.mean(map(lambda p: p.getDt(), points))
    lons = np.mean(lon)
    lats = np.mean(lat)

    genSample = []
    last = points[0]
    for i in range(20):
        p = Point(i*(-1), last.getLat()+lats, last.getLon()+lons, last.getTime(), dts)
        genSample.append(p)
        last = p

    print(genSample)

    return genSample



"""
Smooths a track using the Extended Kalman Filter
"""
def smooth(points):
    measurements = map(lambda p: p.gen2arr(), points)
    dts = map(lambda p: p.getDt(), points)
    dt = np.mean(dts)
    transition = [
            [1, dt, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, dt],
            [0, 0, 0, 1]]
    observation = [
            [1, 0, 0, 0],
            [0, 0, 1, 0]]
    initial = [measurements[0][0], measurements[0][1], 0, 0]
    kf = KalmanFilter(transition_matrices = transition, observation_matrices = observation, initial_state_mean=initial)
    kf = kf.em(measurements, n_iter=5)
    (smoothed_state_means, smoothed_state_covariances) = kf.smooth(measurements)

    for pi, point in enumerate(points):
        point.setLon(smoothed_state_means[pi][0])
        point.setLat(smoothed_state_means[pi][2])

    return points

"""
Simplifies a track using a variant of Ramer Douglas-Peucker
"""
def simplify(gpx):
    return gpx

def main():
    fileName = sys.argv[1]
    file = loadFile(fileName)
    preprocessed = preprocess(file)
    #alls = [item for sublist in segments for item in sublist]
    ps = copy.deepcopy(preprocessed)
    #smoothed = smooth(copy.deepcopy(preprocessed))
    #plotSegments([alls, smoothed], False)
    segments = segment(preprocessed)
    plotSegments(segments, False)

    #ps = sorted(preprocessed, key=lambda point: abs(point.getAcc()))
    #xml = smooth(calculateSpeedAndAccelaration(removeEpoch(file))).to_xml()
    #print(xml)


main()
