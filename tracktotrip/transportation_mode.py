"""
Transportation mode infering
"""
import numpy as np
from changepy import pelt
from changepy.costs import normal_mean

def extract_features(points, n_tops):
    """ Feature extractor

    Args:
        points (:obj:`list` of :obj:`Point`)
        n_tops (int): Number of top speeds to extract
    Returns:
        :obj:`list` of float: with length (n_tops*2). Where the ith even element
            is the ith top speed and the i+1 element is the percentage of time
            spent on that speed
    """
    max_bin = -1
    for point in points:
        max_bin = max(max_bin, point.vel)
    max_bin = int(round(max_bin)) + 1

    # inits histogram
    histogram = [0] * max_bin
    time = 0

    # fills histogram
    for point in points:
        bin_index = int(round(point.vel))
        histogram[bin_index] += point.dt
        time += point.dt

    result = []
    if time == 0:
        return result

    for _ in range(n_tops):
        max_index = np.argmax(histogram)
        value = histogram[max_index] / time
        result.extend([max_index, value])
        histogram[max_index] = -1

    return result

def speed_clustering(clf, points, min_time):
    """ Transportation mode infering, based on changepoint segmentation

    Args:
        clf (:obj:`Classifier`): Classifier to use
        points (:obj:`list` of :obj:`Point`)
        min_time (float): Min time, in seconds, before do another segmentation
    Returns:
        :obj:`list` of :obj:`dict`
    """
    # get changepoint indexes
    data = [p.vel for p in points]
    changepoints = pelt(normal_mean(data, np.std(data)), len(data))

    # Doesn't have change points
    if len(changepoints) == 0:
        changepoints.append(0)

    # insert last point to be a change point
    changepoints.append(len(points) - 1)

    # info for each changepoint
    cp_info = []

    for i in range(0, len(changepoints) - 1):
        from_index = changepoints[i]
        to_index = changepoints[i+1]
        features = extract_features(points[from_index:to_index], clf.feature_length/2)
        if len(features) > 0:
            [probs] = clf.predict([features], verbose=True)
            top_label = sorted(probs.items(), key=lambda val: val[1])
            cp_info.append({
                'from': from_index,
                'to': to_index,
                'classification': probs,
                'label': top_label[-1][0]
                })


    # group based on label
    previous = cp_info[0]
    grouped = []
    # cum_dt = cp_info[0]['dt']

    # TODO: refactor grouping to another function

    for changep in cp_info[1:]:
        if changep['label'] != previous['label']:# and changep['dt'] > min_time:
            previous['to'] = changep['from']
            # previous['dt'] = cum_dt
            grouped.append(previous)
            previous = changep
            # cum_dt = 0
        # cum_dt = cum_dt + changep['dt']
    previous['to'] = cp_info[-1]['to']
    grouped.append(previous)

    return grouped
