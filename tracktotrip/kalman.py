"""
Kalman filter
See https://github.com/open-city/ikalman
"""
import ikalman

def kalman_filter(points, noise):
    """ Smooths points with kalman filter

    See https://github.com/open-city/ikalman

    Args:
        points (:obj:`list` of :obj:`Point`): points to smooth
        noise (float): expected noise
    """
    kalman = ikalman.filter(noise)
    for point in points:
        kalman.update_velocity2d(point.lat, point.lon, point.dt)
        (lat, lon) = kalman.get_lat_long()
        point.lat = lat
        point.lon = lon
    return points
