from .Point import Point
import copy
import numpy as np
from kalman import kalman_filter
import defaults

def extrapolate_points(points, N):
    """Extrapolate a number of points, based on the first ones

    Args:
        points: sample of points to extrapolate
        N: number of points to extrapolate
    Returns:
        Array of tracktotrip.Point
    """
    points = points[:]
    lat = []
    lon = []
    last = None
    for point in points:
        if last!=None:
            lat.append(last.lat-point.lat)
            lon.append(last.lon-point.lon)
        last = point

    dts = np.mean(map(lambda p: p.dt, points))
    lons = np.mean(lon)
    lats = np.mean(lat)

    genSample = []
    last = points[0]
    for i in range(N):
        p = Point(i*(-1), last.lat+lats, last.lon+lons, last.time, dts)
        genSample.append(p)
        last = p

    return genSample

def smooth(points, noise=defaults.SMOOTH_NOISE):
    """ Smooths a set of points based on kalman filter
        See: https://github.com/lacker/ikalman

    Args:
        points: Array of tracktotrip.Point
        noise: Float, optional. Expected noise, the higher it is the
            more the path will be smoothed. Default is 1.0
    """
    return kalman_filter(points, noise)

def smooth_with_extrapolation(points, N=20, noise=defaults.SMOOTH_NOISE):
    """Smooths a set of points, but it extrapolates
    some points at the beginning

    Args:
        points: Array of tracktotrip.Point
        N: number of points to extrapolate
        noise: Float, optional. Expected noise, the higher it is the
            more the path will be smoothed. Default is 1.0
    """
    return smooth(extrapolate_points(points, N) + points, noise=noise)[N:]

def smooth_with_inverse(points, noise=defaults.SMOOTH_NOISE):
    """Smooths a set of points.

    It smooths them twice, once in given order, another one
    in the reverse order.
    The the first half of the results will be taken from the
    reverse order and the second half from the normal order.

    Args:
        points: Array of tracktotrip.Point
        noise: Float, optional. Expected noise, the higher it is the
            more the path will be smoothed. Default is 1.0
    """
    N = len(points)/2
    partOfPoints = copy.deepcopy(points[:N])
    partOfPoints = list(reversed(partOfPoints))
    part = smooth(partOfPoints, noise=noise)
    total = smooth(points, noise=noise)
    noiseSample = 20
    return list(reversed(part))[:N-noiseSample] + total[(N-noiseSample):]

def smooth_segment(segment, strategy="inverse", noise=defaults.SMOOTH_NOISE):
    """Smooths a segment points

    Args:
        segment: tracktotrip.Segment
        strategy: Optional string, strategy to use. Either 'inverse' or
            'extrapolate'. Default is 'inverse'
        noise: Float, optional. Expected noise, the higher it is the
            more the path will be smoothed. Default is 1.0
    """
    E = "extrapolate"
    I = "inverse"
    if strategy == E or strategy == I:
        temp = None
        if strategy == E:
            temp = smooth_with_extrapolation(segment, noise=noise)
        elif strategy == I:
            temp = smooth_with_inverse(segment, noise=noise)
        return temp
    else:
        raise NameError("Invalid startegy, either " + E + " or " + I + ", not " + strategy)
