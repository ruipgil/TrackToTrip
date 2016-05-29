from math import sqrt

def distance(a, b):
    return  sqrt((a.lat - b.lat) ** 2 + (a.lon - b.lon) ** 2)

def point_line_distance(point, start, end):
    if (start == end):
        return distance(point, start)
    else:
        n = abs(
            (end.lat - start.lat) * (start.lon - point.lon) - (start.lat - point.lat) * (end.lon - start.lon)
        )
        d = sqrt(
            (end.lat - start.lat) ** 2 + (end.lon - start.lon) ** 2
        )
        return n / d

def drp(points, epsilon):
    dmax = 0.0
    index = 0

    for i in range(1, len(points)-1):
        d = point_line_distance(points[i], points[0], points[-1])
        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        return drp(points[:index+1], epsilon)[:-1] + drp(points[index:], epsilon)
    else:
        return [points[0], points[-1]]

