from .Point import Point
import datetime

MAX_ACC = 30.2

def PointAccessor(point):
    return point.lat, point.lon, point.time

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

            if abs(thisPoint.acc) > maxAcc:
                thisPoint = Point(pi, lat=lastPoint.lat, lon=lastPoint.lon, time=ptime)
                thisPoint.computeMetrics(lastPoint)
                skipped.append((thisPoint, thisPoint.acc))

            result.append(thisPoint)
            lastPoint = thisPoint
        else:
            skipped.append(thisPoint)

    return result, skipped

def shouldRemoveEpoch(gpxPoint):
    return gpxPoint.time < datetime.datetime(1999, 1, 1)

