"""
Smoothing methods
"""
import copy
import numpy as np
from .point import Point
from .kalman import kalman_filter

INVERSE_STRATEGY = 0
EXTRAPOLATE_STRATEGY = 1

def extrapolate_points(points, n_points):
    """ Extrapolate a number of points, based on the first ones

    Args:
        points (:obj:`list` of :obj:`Point`)
        n_points (int): number of points to extrapolate
    Returns:
        :obj:`list` of :obj:`Point`
    """
    points = points[:]
    lat = []
    lon = []
    last = None
    for point in points:
        if last is not None:
            lat.append(last.lat-point.lat)
            lon.append(last.lon-point.lon)
        last = point

    dts = np.mean([p.dt for p in points])
    lons = np.mean(lon)
    lats = np.mean(lat)

    gen_sample = []
    last = points[0]
    for _ in range(n_points):
        point = Point(last.lat+lats, last.lon+lons, last.time - dts)
        point.compute_metrics(last)
        gen_sample.append(point)
        last = point

    return gen_sample

def with_extrapolation(points, noise, n_points):
    """ Smooths a set of points, but it extrapolates some points at the beginning

    Args:
        points (:obj:`list` of :obj:`Point`)
        noise (float): Expected noise, the higher it is the more the path will
            be smoothed.
    Returns:
        :obj:`list` of :obj:`Point`
    """
    return kalman_filter(extrapolate_points(points, n_points) + points, noise)[n_points:]

def with_inverse(points, noise):
    """ Smooths a set of points

    It smooths them twice, once in given order, another one in the reverse order.
    The the first half of the results will be taken from the reverse order and
        the second half from the normal order.

    Args:
        points (:obj:`list` of :obj:`Point`)
        noise (float): Expected noise, the higher it is the more the path will
            be smoothed.
    Returns:
        :obj:`list` of :obj:`Point`
    """
    noise_sample = 20
    n_points = len(points)/2
    break_point = n_points - noise_sample

    points_part = copy.deepcopy(points[:n_points])
    points_part = list(reversed(points_part))
    part = kalman_filter(points_part, noise)
    total = kalman_filter(points, noise)

    return list(reversed(part))[:break_point] + total[break_point:]
