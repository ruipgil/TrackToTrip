from .Point import Point
import copy
import numpy as np
from pykalman import KalmanFilter

def extrapolatePoints(points, N):
    points = points[:]
    lat = []
    lon = []
    last = None
    for point in points:
        if last!=None:
            lat.append(last.getLat()-point.getLat())
            lon.append(last.getLon()-point.getLon())
        last = point

    dts = np.mean(map(lambda p: p.getDt(), points))
    lons = np.mean(lon)
    lats = np.mean(lat)

    genSample = []
    last = points[0]
    for i in range(N):
        p = Point(i*(-1), last.getLat()+lats, last.getLon()+lons, last.getTime(), dts)
        genSample.append(p)
        last = p

    return genSample



"""
Smooths a track using the Extended Kalman Filter
"""
def smooth(points, n_iter=5):
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
    kf = kf.em(measurements, n_iter=n_iter)
    (smoothed_state_means, smoothed_state_covariances) = kf.smooth(measurements)

    for pi, point in enumerate(points):
        point.setLon(smoothed_state_means[pi][0])
        point.setLat(smoothed_state_means[pi][2])

    return points

def smoothWithExtrapolation(points, N=20, n_iter=2):
    return smooth(extrapolatePoints(points, N) + points, n_iter=n_iter)[N:]

def smoothWithInverse(points, N=100, n_iter=2):
    partOfPoints = copy.deepcopy(points[:N])
    part = smooth(list(reversed(partOfPoints)))
    total = smooth(points)
    noiseSample = 20
    return list(reversed(part))[:N-noiseSample] + total[(N-noiseSample):]

