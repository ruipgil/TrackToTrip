"""
Time-distance compression algorithms
"""
from .point import Point

def loc_dist(end, start):
    """ Spatial distance between two points (end-start)

    Args:
        start (:obj:`Point`)
        end (:obj:`Point`)
    Returns:
        float, distance in m
    """
    return end.distance(start)

def time_dist(end, start):
    """ Temporal distance between two points (end-start)

    Args:
        start (:obj:`Point`)
        end (:obj:`Point`)
    Returns:
        float, time difference in seconds
    """
    return end.time_difference(start)

def td_sp(points, speed_threshold):
    """ Top-Down Speed-Based Trajectory Compression Algorithm

    Detailed in https://www.itc.nl/library/Papers_2003/peer_ref_conf/meratnia_new.pdf

    Args:
        points (:obj:`list` of :obj:`Point`): trajectory or part of it
        speed_threshold (float): speed threshold
    Returns:
        :obj:`list` of :obj:`Point`, compressed trajectory
    """
    if len(points) <= 2:
        return points
    else:
        max_speed_threshold = 0
        found_index = 0
        for i in range(1, len(points)-1):
            dt1 = time_dist(points[i], points[i-1])
            if dt1 == 0:
                dt1 = 0.000000001
            vim = loc_dist(points[i], points[i-1]) / dt1
            dt2 = time_dist(points[i+1], points[i])
            if dt2 == 0:
                dt2 = 0.000000001
            vi_ = loc_dist(points[i+1], points[i]) / dt2
            if abs(vi_ - vim) > max_speed_threshold:
                max_speed_threshold = abs(vi_ - vim)
                found_index = i
        if max_speed_threshold > speed_threshold:
            one = td_sp(points[:found_index], speed_threshold)
            two = td_sp(points[found_index:], speed_threshold)
            one.extend(two)
            return one
        else:
            return [points[0], points[-1]]

def td_tr(points, dist_threshold):
    """ Top-Down Time-Ratio Trajectory Compression Algorithm

    Detailed in https://www.itc.nl/library/Papers_2003/peer_ref_conf/meratnia_new.pdf

    Args:
        points (:obj:`list` of :obj:`Point`): trajectory or part of it
        dist_threshold (float): distance threshold
    Returns:
        :obj:`list` of :obj:`Point`, compressed trajectory
    """
    if len(points) <= 2:
        return points
    else:
        max_dist_threshold = 0
        found_index = 0
        delta_e = time_dist(points[-1], points[0]) / 3600
        d_lat = points[-1].lat - points[0].lat
        d_lon = points[-1].lon - points[0].lon

        for i in range(1, len(points)-1):
            delta_i = time_dist(points[i], points[0]) / 3600

            di_de = delta_i / delta_e
            point = Point(
                points[0].lat + d_lat * di_de,
                points[0].lon + d_lon * di_de,
                None
            )

            dist = loc_dist(points[i], point)
            if dist > max_dist_threshold:
                max_dist_threshold = dist
                found_index = i

        if max_dist_threshold > dist_threshold:
            one = td_tr(points[:found_index], dist_threshold)
            two = td_tr(points[found_index:], dist_threshold)
            one.extend(two)
            return one
        else:
            return [points[0], points[-1]]
