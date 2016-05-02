def inferTransportationMode(points):
    tmodes = naiveTransportationInferring(points)
    tgroup = group(tmodes)
    result = []
    for j, (i, tm) in enumerate(tgroup):
        if len(tgroup) <= j + 1:
            end, _ = tgroup[j]
        else:
            end, _ = tgroup[j + 1]
        # if tm != 'Stop':
        result.append({
            'label': tm,
            'from': i,
            'to': end
            })
    return result

def naiveTransportationInferring(points, S = 0.1, W = 7):
    """Infers the transportation mode of a set of points
    based on their velocity.

    The following association will be made between velocity
    and transportation modes:
    + 0 <= vel < S km/h : stationary
    + S <= vel < W km/h : on foot
    + W <= vel km/h     : on vehicle
    The default values for those transportation modes are:
    + S: 1 km/h
    + W: 5.5 km/h
    """

    tmodes = []
    for point in points:
        vel = point.vel
        if 0 <= vel and vel < S:
            tmodes.append('Stop')
        elif S <= vel and vel < W:
            tmodes.append('Foot')
        else:
            tmodes.append('Vehicle')

    return tmodes

def group(modes):
    last = None
    grp = []
    for i, mode in enumerate(modes):
        if last != mode:
            grp.append((i, mode))
            last = mode
    return grp
