# py_kalman from https://github.com/open-city/ikalman
import py_kalman

def kalman_filter(points, noise=1.0):
    kf = py_kalman.filter(noise)
    for point in points:
        kf.update_velocity2d(point.lat, point.lon, point.dt)

        (lat, lon) = kf.get_lat_long()
        point.lat = lat
        point.lon = lon
    return points

