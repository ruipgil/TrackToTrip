from .Point import Point
import copy
import numpy as np
from scipy import stats
from kalman import kalman_filter

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

def smooth(points, n_iter=5):
    """Smooths a set of points

    Args:
        points: Array of tracktotrip.Point
        n_iter: number of iterations for the expectation-maximixation
            algorithm
    """
    measurements = map(lambda p: p.gen2arr(), points)
    dts = map(lambda p: p.dt, points)
    dt = stats.mode(dts).mode[0]

    smoothed = kalman_filter(measurements, dt, n_iter)
    for pi, point in enumerate(points):
        point.lon = smoothed[pi][0]
        point.lat = smoothed[pi][1]
    return points

def smooth_with_extrapolation(points, N=20, n_iter=2):
    """Smooths a set of points, but it extrapolates
    some points at the beginning

    Args:
        points: Array of tracktotrip.Point
        N: number of points to extrapolate
        n_iter: number of iterations for the expectation-maximization
            algorithm
    """
    return smooth(extrapolate_points(points, N) + points, n_iter=n_iter)[N:]

def smooth_with_inverse(points, n_iter=2):
    """Smooths a set of points.

    It smooths them twice, once in given order, another one
    in the reverse order.
    The the first half of the results will be taken from the
    reverse order and the second half from the normal order.

    Args:
        points: Array of tracktotrip.Point
        n_iter: number of iterations for the expectation-maximization
            algorithm
    """
    N = len(points)/2
    partOfPoints = copy.deepcopy(points[:N])
    part = smooth(list(reversed(partOfPoints)))
    total = smooth(points)
    noiseSample = 20
    return list(reversed(part))[:N-noiseSample] + total[(N-noiseSample):]

def smooth_segment(segment, strategy="inverse", n_iter=2):
    """Smooths a segment points

    Args:
        segment: tracktotrip.Segment
        strategy: Optional string, strategy to use. Either 'inverse' or
            'extrapolate'. Default is 'inverse'
    """
    E = "extrapolate"
    I = "inverse"
    if strategy == E or strategy == I:
        temp = None
        if strategy == E:
            temp = smooth_with_extrapolation(segment)
        elif strategy == I:
            temp = smooth_with_inverse(segment)
        # print('smoothing', temp)
        return temp
    else:
        raise NameError("Invalid startegy, either " + E + " or " + I + ", not " + strategy)
