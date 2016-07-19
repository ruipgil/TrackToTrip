"""
Douglas ramer peucker
"""

from math import sqrt

def distance(p_a, p_b):
    """ Euclidean distance, between two points

    Args:
        p_a (:obj:`Point`)
        p_b (:obj:`Point`)
    Returns:
        float: distance, in degrees
    """
    return sqrt((p_a.lat - p_b.lat) ** 2 + (p_a.lon - p_b.lon) ** 2)

def point_line_distance(point, start, end):
    """ Distance from a point to a line, formed by two points

    Args:
        point (:obj:`Point`)
        start (:obj:`Point`): line point
        end (:obj:`Point`): line point
    Returns:
        float: distance to line, in degrees
    """
    if start == end:
        return distance(point, start)
    else:
        un_dist = abs(
            (end.lat-start.lat)*(start.lon-point.lon) - (start.lat-point.lat)*(end.lon-start.lon)
        )
        n_dist = sqrt(
            (end.lat-start.lat)**2 + (end.lon-start.lon)**2
        )
        return un_dist / n_dist

def drp(points, epsilon):
    """ Douglas ramer peucker

    Based on https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm

    Args:
        points (:obj:`list` of :obj:`Point`)
        epsilon (float): drp threshold
    Returns:
        :obj:`list` of :obj:`Point`
    """
    dmax = 0.0
    index = 0

    for i in range(1, len(points)-1):
        dist = point_line_distance(points[i], points[0], points[-1])
        if dist > dmax:
            index = i
            dmax = dist

    if dmax > epsilon:
        return drp(points[:index+1], epsilon)[:-1] + drp(points[index:], epsilon)
    else:
        return [points[0], points[-1]]
