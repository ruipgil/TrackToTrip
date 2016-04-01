from .Point import Point
import copy
import datetime

MAX_ACC = 30.2

def PointAccessor(point):
    return point.getLat(), point.getLon(), point.getTime()

def preprocessSegment(arrayOfPoints, accessor=PointAccessor, maxAcc=MAX_ACC):
    result = []
    skipped = []
    lastPoint = None
    for pi, point in enumerate(arrayOfPoints):
        if not shouldRemoveEpoch(point):
            plat, plon, ptime = accessor(point)
            thisPoint = Point(pi, lat=plat, lon=plon, time=ptime)

            if lastPoint != None:
                thisPoint.computeMetrics(lastPoint)

            if abs(thisPoint.getAcc()) > maxAcc:
                thisPoint = Point(pi, lat=lastPoint.getLat(), lon=lastPoint.getLon(), time=ptime)
                thisPoint.computeMetrics(lastPoint)
                skipped.append((thisPoint, thisPoint.getAcc()))

            result.append(thisPoint)
            lastPoint = thisPoint
        else:
            skipped.append(thisPoint)

    return result, skipped

def preprocess_(arrayOfSegments, accessor, maxAcc=MAX_ACC):
    result = []
    skipped = []
    lastPoint = None
    for si, arrayOfPoints in enumerate(arrayOfSegments):
        for pi, point in enumerate(arrayOfPoints):
            if not shouldRemoveEpoch(point):
                plat, plon, ptime = accessor(point)
                thisPoint = Point(pi, lat=plat, lon=plon, time=ptime)

                if lastPoint != None:
                    thisPoint.computeMetrics(lastPoint)

                if abs(thisPoint.getAcc()) > maxAcc:
                    thisPoint = Point(pi, lat=lastPoint.getLat(), lon=lastPoint.getLon(), time=ptime)
                    thisPoint.computeMetrics(lastPoint)
                    skipped.append((thisPoint, thisPoint.getAcc()))

                result.append(thisPoint)
                lastPoint = thisPoint


    return result, skipped

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
                        result.append(thisPoint)
                        lastPoint = thisPoint
                        lastGpxPoint = point

                    else:
                        thisPoint = Point(pi, lastGpxPoint.latitude, lastGpxPoint.longitude, point.time, point.time_difference(lastGpxPoint))
                        result.append(thisPoint)
                        lastPoint = thisPoint
                        temp = copy.deepcopy(point)
                        temp.latitude = lastGpxPoint.latitude
                        temp.longitude = lastGpxPoint.longitude
                        lastGpxPoint = temp
                        #print("dropped " + str(thisPoint))
                        cc = cc + 1
    #print("acc removed " + str(cc))
    return result

def shouldRemoveEpoch(gpxPoint):
    return gpxPoint.getTime() < datetime.datetime(1999, 1, 1)

def createPointFromGPX(i, point):
    return Point(i, point.latitude, point.longitude, point.time)

def createPointFromGPXs(i, point, previousGpx, previous):
    dt = point.time_difference(previousGpx)
    vel = 0
    dv = 0
    acc = 0
    if dt != 0 :
        vel = point.distance_2d(previousGpx)/dt
        dv = vel - previous.getVel()
        acc = dv/dt
    return Point(i, point.latitude, point.longitude, point.time, dt, acc, vel)
