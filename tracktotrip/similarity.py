"""
Similarity functions
"""
import math
import numpy as np
from rtree import index

#pylint: disable=invalid-name

def dot(p1, p2):
    """Dot product between two points

    Args:
        p1 ([float, float]): x and y coordinates
        p2 ([float, float]): x and y coordinates
    Returns:
        float
    """
    return p1[0] * p2[0] + p1[1] * p2[1]

def normalize(p):
    """Normalizes a point/vector

    Args:
        p ([float, float]): x and y coordinates
    Returns:
        float
    """
    l = math.sqrt(p[0]**2 + p[1]**2)
    return [p[0]/l, p[1]/l]

def angle(p1, p2):
    """Angle between two points

    Args:
        p1 ([float, float]): x and y coordinates
        p2 ([float, float]): x and y coordinates
    Returns:
        float
    """
    return dot(p1, p2)

def angle_similarity(l1, l2):
    """Computes the similarity between two lines, based
    on their angles

    Args:
        l1 ([float, float]): x and y coordinates
        l2 ([float, float]): x and y coordinates
    Returns:
        float
    """
    return angle(l1, l2)

def line(p1, p2):
    """Creates a line from two points

    From http://stackoverflow.com/a/20679579

    Args:
        p1 ([float, float]): x and y coordinates
        p2 ([float, float]): x and y coordinates
    Returns:
        (float, float, float): x, y and _
    """
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def intersection(L1, L2):
    """Intersects two line segments

    Args:
        L1 ([float, float]): x and y coordinates
        L2 ([float, float]): x and y coordinates
    Returns:
        bool: if they intersect
        (float, float): x and y of intersection, if they do
    """
    D = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x, y
    else:
        return False

def distance(a, b):
    """Distance between two points

    Args:
        a ([float, float]): x and y coordinates
        b ([float, float]): x and y coordinates
    Returns:
        float
    """
    return math.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2)

def distance_tt_point(a, b):
    """ Euclidean distance between two (tracktotrip) points

    Args:
        a (:obj:`Point`)
        b (:obj:`Point`)
    Returns:
        float
    """
    return math.sqrt((b.lat-a.lat)**2 + (b.lon-a.lon)**2)

def closest_point(a, b, p):
    """Finds closest point in a line segment

    Args:
        a ([float, float]): x and y coordinates. Line start
        b ([float, float]): x and y coordinates. Line end
        p ([float, float]): x and y coordinates. Point to find in the segment
    Returns:
        (float, float): x and y coordinates of the closest point
    """
    ap = [p[0]-a[0], p[1]-a[1]]
    ab = [b[0]-a[0], b[1]-a[1]]
    mag = float(ab[0]**2 + ab[1]**2)
    proj = dot(ap, ab)
    dist = proj / mag
    if dist < 0:
        return [a[0], a[1]]
    elif dist > 1:
        return [b[0], b[1]]
    else:
        return [a[0] + ab[0] * dist, a[1] + ab[1] * dist]

def distance_to_line(a, b, p):
    """Closest distance between a line segment and a point

    Args:
        a ([float, float]): x and y coordinates. Line start
        b ([float, float]): x and y coordinates. Line end
        p ([float, float]): x and y coordinates. Point to compute the distance
    Returns:
        float
    """
    return distance(closest_point(a, b, p), p)

CLOSE_DISTANCE_THRESHOLD = 1.0
def distance_similarity(a, b, p, T=CLOSE_DISTANCE_THRESHOLD):
    """Computes the distance similarity between a line segment
    and a point

    Args:
        a ([float, float]): x and y coordinates. Line start
        b ([float, float]): x and y coordinates. Line end
        p ([float, float]): x and y coordinates. Point to compute the distance
    Returns:
        float: between 0 and 1. Where 1 is very similar and 0 is completely different
    """
    d = distance_to_line(a, b, p)
    r = (-1/float(T)) * abs(d) + 1

    return r if r > 0 else 0

def line_distance_similarity(p1a, p1b, p2a, p2b, T=CLOSE_DISTANCE_THRESHOLD):
    """Line distance similarity between two line segments

    Args:
        p1a ([float, float]): x and y coordinates. Line A start
        p1b ([float, float]): x and y coordinates. Line A end
        p2a ([float, float]): x and y coordinates. Line B start
        p2b ([float, float]): x and y coordinates. Line B end
    Returns:
        float: between 0 and 1. Where 1 is very similar and 0 is completely different
    """
    d1 = distance_similarity(p1a, p1b, p2a, T=T)
    d2 = distance_similarity(p1a, p1b, p2b, T=T)
    return abs(d1 + d2) * 0.5

def line_similarity(p1a, p1b, p2a, p2b, T=CLOSE_DISTANCE_THRESHOLD):
    """Similarity between two lines

    Args:
        p1a ([float, float]): x and y coordinates. Line A start
        p1b ([float, float]): x and y coordinates. Line A end
        p2a ([float, float]): x and y coordinates. Line B start
        p2b ([float, float]): x and y coordinates. Line B end
    Returns:
        float: between 0 and 1. Where 1 is very similar and 0 is completely different
    """
    d = line_distance_similarity(p1a, p1b, p2a, p2b, T=T)
    a = abs(angle_similarity(normalize(line(p1a, p1b)), normalize(line(p2a, p2b))))
    return d * a

def bounding_box_from(points, i, i1):
    """Creates bounding box for a line segment

    Args:
        points (:obj:`list` of :obj:`Point`)
        i (int): Line segment start, index in points array
        i1 (int): Line segment end, index in points array
    Returns:
        (float, float, float, float): with bounding box min x, min y, max x and max y
    """
    pi = points[i]
    pi1 = points[i1]

    min_lat = min(pi.lat, pi1.lat)
    min_lon = min(pi.lon, pi1.lon)
    max_lat = max(pi.lat, pi1.lat)
    max_lon = max(pi.lon, pi1.lon)

    latd = (max_lat-min_lat) * 2
    lond = (max_lon-min_lon) * 2

    return min_lat-latd, min_lon-lond, max_lat+latd, max_lon+lond

def segment_similarity(A, B):
    """Computes the similarity between two segments

    Args:
        A (:obj:`Segment`)
        B (:obj:`Segment`)
    Returns:
        float: between 0 and 1. Where 1 is very similar and 0 is completely different
    """
    l_a = len(A.points)
    l_b = len(B.points)

    idx = index.Index()
    dex = 0
    for i in range(l_a-1):
        idx.insert(dex, bounding_box_from(A.points, i, i+1), obj=[A.points[i], A.points[i+1]])
        dex = dex + 1

    prox_acc = []

    for i in range(l_b-1):
        ti = B.points[i].gen2arr()
        ti1 = B.points[i+1].gen2arr()
        bb = bounding_box_from(B.points, i, i+1)
        intersects = idx.intersection(bb, objects=True)
        # print("Intersecting %s %s" % (ti, ti1))
        n_prox = []
        i_prox = 0
        a = 0
        for x in intersects:
            a = a + 1
            pi = x.object[0].gen2arr()
            pi1 = x.object[1].gen2arr()
            prox = line_similarity(ti, ti1, pi, pi1)
            i_prox = i_prox + prox
            n_prox.append(prox)
            # print(pi, pi1, prox)

        if a != 0:
            # prox_acc.append(i_prox / a)
            prox_acc.append(max(n_prox))
        else:
            prox_acc.append(0)

    return np.mean(prox_acc), prox_acc

def sort_segment_points(Aps, Bps):
    """Takes two line segments and sorts all their points,
    so that they form a continuous path

    Args:
        Aps: Array of tracktotrip.Point
        Bps: Array of tracktotrip.Point
    Returns:
        Array with points ordered
    """
    mid = []
    j = 0
    mid.append(Aps[0])
    for i in range(len(Aps)-1):
        dist = distance_tt_point(Aps[i], Aps[i+1])
        for m in range(j, len(Bps)):
            distm = distance_tt_point(Aps[i], Bps[m])
            if dist < distm:
                j = m
                break
            mid.append(Bps[m])

        mid.append(Aps[i+1])
    for m in range(j, len(Bps)):
        mid.append(Bps[m])
    return mid
