import math
from datetime import timedelta

def get_line_equation_coefficients(location1, location2):
    if location1.getLon() == location2.getLon():
        # Vertical line:
        return float(0), float(1), float(-location1.getLon())
    else:
        a = float(location1.getLat() - location2.getLat()) / (location1.getLon() - location2.getLon())
        b = location1.getLat() - location1.getLon() * a
        return float(1), float(-a), float(-b)

def distance_from_line(point, line_point_1, line_point_2):
    a = line_point_1.distance(line_point_2)

    if a == 0:
        return line_point_1.distance(point), line_point_2.getTime()-line_point_1.getTime()

    b = line_point_1.distance(point)
    c = line_point_2.distance(point)

    s = (a + b + c) / 2.

    return 2. * math.sqrt(abs(s * (s - a) * (s - b) * (s - c))) / a, line_point_2.getTime()-line_point_1.getTime()


def simplify(points, max_distance, max_time):
    if len(points) < 3:
        return points

    begin, end = points[0], points[-1]

    a, b, c = get_line_equation_coefficients(begin, end)
    #t = end.getTime()-begin.getTime()

    tmp_max_distance = -1000000
    tmp_max_distance_position = None

    for point_no in range(len(points[1:-1])):
        point = points[point_no]
        d = abs(a * point.getLat() + b * point.getLon() + c)

        if d > tmp_max_distance:
            tmp_max_distance = d
            tmp_max_distance_position = point_no


    # Now that we have the most distance point, compute its real distance:
    real_max_distance, real_time = distance_from_line(points[tmp_max_distance_position], begin, end)

    #print real_time
    if real_max_distance < max_distance or real_time < timedelta(seconds=max_time):
        return [begin, end]

    return (simplify(points[:tmp_max_distance_position + 2], max_distance, max_time) +
            simplify(points[tmp_max_distance_position + 1:], max_distance, max_time)[1:])
