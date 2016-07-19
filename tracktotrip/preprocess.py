"""
Segment preprocessing
"""
import datetime
from .point import Point

MIN_TIME = datetime.datetime(1999, 1, 1)

def preprocess_segment(points, max_acc, destructive=True):
    """ Calculates the metrics of points and unrealistic ones

    Uses their ordering to calculate velocities and spatio-temporal distances
    If destructive it removes points with accelarations higher than max_acc
        and that occured before MIN_TIME

    Args:
        points (:obj:`list` of :obj:`Point`)
        max_acc (float): Maximum acceleration threshold
        destructive (bool, optional): True to allow the removal of elements
            from the initial array. Default is True
    Returns:
        A tuple with the resulting array of points and the
        the points dropped
    """
    result = []
    last = None
    for point in points:
        if not (destructive and point.time < MIN_TIME):
            current = Point(point.lat, point.lon, point.time)

            if last is not None:
                current.compute_metrics(last)

            if destructive and abs(current.acc) > max_acc:
                current = Point(last.lat, last.lon, point.time)
                current.compute_metrics(last)

            result.append(current)
            last = current

    return result
