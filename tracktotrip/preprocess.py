from .Point import Point
import datetime

MAX_ACC = 30.2
MIN_TIME = datetime.datetime(1999, 1, 1)

def preprocessSegment(arrayOfPoints, destructive=True, accessor=Point.accessor, maxAcc=MAX_ACC):
    """Calculates the metrics of points

    Uses their ordering to calculate velocities and
    spatio-temporal distances
    If destructive it removes points with accelarations
    higher than maxAcc and that occured before MIN_TIME

    Args:
        arrayOfPoints: Array of TrackToTrip.Point
        destructive: Optional, boolean. True to allow
            the removal of elements from the initial
            array. Default is True
        accessor: Optional, function. Latitude, longitude
            and time properties getter. Default is
            TrackToTrip.Point.accessor
        maxAcc: Optional, number. Drop points with an
            accelaration above maxAcc. Defaul is MAX_ACC
    Returns:
        A tuple with the resulting array of points and the
        the points dropped
    """
    result = []
    skipped = []
    lastPoint = None
    for pi, point in enumerate(arrayOfPoints):
        if not shouldRemoveEpoch(point, destructive):
            plat, plon, ptime = accessor(point)
            thisPoint = Point(pi, lat=plat, lon=plon, time=ptime)

            if lastPoint != None:
                thisPoint.computeMetrics(lastPoint)

            if destructive and abs(thisPoint.acc) > maxAcc:
                thisPoint = Point(pi, lat=lastPoint.lat, lon=lastPoint.lon, time=ptime)
                thisPoint.computeMetrics(lastPoint)
                skipped.append((thisPoint, thisPoint.acc))

            result.append(thisPoint)
            lastPoint = thisPoint
        else:
            skipped.append(thisPoint)

    return result, skipped

def shouldRemoveEpoch(gpxPoint, destructive):
    return destructive and gpxPoint.time < MIN_TIME

