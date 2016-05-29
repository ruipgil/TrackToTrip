import math
import numpy as np

def dot(p1, p2):
    """Dot product between two points

    Args:
        p1: Array of numbers, with x and y coordinates
        p2: Array of numbers, with x and y coordinates
    Returns:
        Number
    """
    return p1[0] * p2[0] + p1[1] * p2[1]

def normalize(p):
    """Normalizes a point/vector

    Args:
        p: Array of numbers, with x and y coordinates
    Returns:
        A new array of numbers
    """
    l = math.sqrt(p[0]**2 + p[1]**2)
    return [p[0]/l, p[1]/l]

def angle(p1, p2):
    """Angle between two points

    Args:
        p1: Array of numbers, with x and y coordinates
        p2: Array of numbers, with x and y coordinates
    Returns:
        Number
    """
    return dot(p1, p2)

def angle_similarity(l1, l2):
    """Computes the similarity between two lines, based
    on their angles

    Args:
        l1: Array of numbers, with x and y coordinates
        l2: Array of numbers, with x and y coordinates
    Returns:
        Number
    """
    return angle(l1, l2)

# from http://stackoverflow.com/a/20679579
def line(p1, p2):
    """Creates a line from two points

    Args:
        p1: Array of numbers, with x and y coordinates
        p2: Array of numbers, with x and y coordinates
    Returns:
        Three-tuple with (x, y and _)
    """
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def intersection(L1, L2):
    """Intersects two line segments

    Args:
        L1: Array of numbers, with x and y coordinates
        L2: Array of numbers, with x and y coordinates
    Returns:
        False if the lines don't intersect, a (x, y) tuple
        if they do
    """
    D  = L1[0] * L2[1] - L1[1] * L2[0]
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
        a: Array of numbers, with x and y coordinates
        b: Array of numbers, with x and y coordinates
    Returns:
        Number
    """
    return math.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2)

def distance_tt_point(a, b):
    return math.sqrt((b.lat-a.lat)**2 + (b.lon-a.lon)**2)

def closestPoint(a, b, p):
    """Finds closest point in a line segment

    Args:
        a: Array of numbers, with x and y coordinates.
            Line start
        b: Array of numbers, with x and y coordinates.
            Line end
        p: Array of numbers, with x and y coordinates.
            Point to find in the segment
    Returns:
        Array of number, with x and y coordinates
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

def distanceToLine(a, b, p):
    """Closest distance between a line segment and a point

    Args:
        a: Array of numbers, with x and y coordinates.
            Line start
        b: Array of numbers, with x and y coordinates.
            Line end
        p: Array of numbers, with x and y coordinates.
            Point to compute the distance
    Returns:
        Number
    """
    return distance(closestPoint(a, b, p), p)

CLOSE_DISTANCE_THRESHOLD = 1.0
def distance_similarity(a, b, p, T=CLOSE_DISTANCE_THRESHOLD):
    """Computes the distance similarity between a line segment
    and a point

    Args:
        a: Array of numbers, with x and y coordinates.
            Line start
        b: Array of numbers, with x and y coordinates.
            Line end
        p: Array of numbers, with x and y coordinates.
            Point to compute the distance
    Returns:
        Number, between 0 and 1. Where 1 is very similar
    """
    d = distanceToLine(a, b, p)
    r = (-1/float(T)) * abs(d) + 1

    return r if r > 0 else 0

def lineDistance_similarity(p1a, p1b, p2a, p2b, T=CLOSE_DISTANCE_THRESHOLD):
    """Line distance similarity between two line segments

    Args:
        p1a: Array of numbers, with x and y coordinates.
            Line A start
        p1b: Array of numbers, with x and y coordinates.
            Line A end
        p2a: Array of numbers, with x and y coordinates.
            Line B start
        p2b: Array of numbers, with x and y coordinates.
            Line B end
    Returns:
        Number, between 0 and 1. Where 1 is very similar
    """
    d1 = distance_similarity(p1a, p1b, p2a, T=T)
    d2 = distance_similarity(p1a, p1b, p2b, T=T)
    return abs(d1 + d2) * 0.5

def line_similarity(p1a, p1b, p2a, p2b, T=CLOSE_DISTANCE_THRESHOLD):
    """Similarity between two lines

    Args:
        p1a: Array of numbers, with x and y coordinates.
            Line A start
        p1b: Array of numbers, with x and y coordinates.
            Line A end
        p2a: Array of numbers, with x and y coordinates.
            Line B start
        p2b: Array of numbers, with x and y coordinates.
            Line B end
    Returns:
        Number, between 0 and 1. Where 1 is very similar
    """
    d = lineDistance_similarity(p1a, p1b, p2a, p2b, T=T)
    a = abs(angle_similarity(normalize(line(p1a, p1b)), normalize(line(p2a, p2b))))
    return d * a

def boundingBoxFrom(points, i, i1):
    """Creates bounding box for a line segment

    Args:
        points: Array with tracktotrip.Point instances
        i: Line segment start, index in points array
        i1: Line segment end, index in points array
    Returns:
        Four-tuple with bounding box (min x, min y, max x, max y)
    """
    pi = points[i]
    pi1 = points[i1]

    minLat = min(pi.lat, pi1.lat)
    minLon = min(pi.lon, pi1.lon)
    maxLat = max(pi.lat, pi1.lat)
    maxLon = max(pi.lon, pi1.lon)

    latd = (maxLat-minLat) * 2
    lond = (maxLon-minLon) * 2

    return minLat-latd, minLon-lond, maxLat+latd, maxLon+lond

from rtree import index
def segment_similarity(A, B):
    """Computes the similarity between two segments

    Args:
        A: tracktotrip.Segment
        B: tracktotrip.Segment
    Returns:
        Number, between 0 and 1. Where 1 is very similar
    """
    lA = len(A.points)
    lB = len(B.points)

    idx = index.Index()
    dex = 0
    for i in range(lA-1):
        idx.insert(dex, boundingBoxFrom(A.points, i, i+1), obj=[A.points[i], A.points[i+1]])
        dex = dex + 1

    prox_acc = []

    for i in range(lB-1):
        ti = B.points[i].gen2arr()
        ti1 = B.points[i+1].gen2arr()
        bb = boundingBoxFrom(B.points, i, i+1)
        intersection = idx.intersection(bb, objects=True)
        # print("Intersecting %s %s" % (ti, ti1))
        n_prox = []
        i_prox = 0
        a = 0
        for x in intersection:
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

    # print(prox_acc)

    return np.mean(prox_acc), prox_acc

def sortSegmentPoints(Aps, Bps):
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
