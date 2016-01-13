from .Point import Point
import copy
import datetime

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


def createPointFromGPX(i, point):
    return Point(i, point.latitude, point.longitude, point.time)

def createPointFromGPXs(i, point, previousGpx, previous):
    dt = point.time_difference(previousGpx)
    vel = point.distance_2d(previousGpx)/dt
    dv = vel - previous.getVel()
    acc = dv/dt
    return Point(i, point.latitude, point.longitude, point.time, dt, acc, vel)
