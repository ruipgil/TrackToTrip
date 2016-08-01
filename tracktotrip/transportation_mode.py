"""
Transportation mode infering
"""
import numpy as np
from changepy import pelt
from changepy.costs import normal_mean
from .utils import pairwise

def learn_transportation_mode(track, clf):
    """ Inserts transportation modes of a track into a classifier

    Args:
        track (:obj:`Track`)
        clf (:obj:`Classifier`)
    """
    for segment in track.segments:
        tmodes = segment.transportation_modes
        points = segment.points
        features = []
        labels = []

        for tmode in tmodes:
            points_part = points[tmode['from']:tmode['to']]
            if len(points_part) > 0:
                features.append(extract_features(points_part, clf.feature_length/2))
                labels.append(tmode['label'])

        clf.learn(features, labels)

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

def speed_difference(points):
    """ Computes the speed difference between each adjacent point

    Args:
        points (:obj:`Point`)
    Returns:
        :obj:`list` of int: Indexes of changepoints
    """
    data = [0]
    for before, after in pairwise(points):
        data.append(before.vel - after.vel)
    return data

def detect_changepoints(points, min_time, data_processor=speed_difference):
    """ Detects changepoints on points that have at least a specific duration

    Args:
        points (:obj:`Point`)
        min_time (float): Min time that a sub-segmented, bounded by two changepoints, must have
        data_processor (function): Function to extract data to feed to the changepoint algorithm.
            Defaults to `speed_difference`
    Returns:
        :obj:`list` of int: Indexes of changepoints
    """
    data = data_processor(points)
    changepoints = pelt(normal_mean(data, np.std(data)), len(data))
    changepoints.append(len(points) - 1)

    result = []
    for start, end in pairwise(changepoints):
        time_diff = points[end].time_difference(points[start])
        if time_diff > min_time:
            result.append(start)

    # adds the first point
    result.append(0)
    # adds the last changepoint detected
    result.append(len(points) - 1)
    return sorted(list(set(result)))

def group_modes(modes):
    """ Groups consecutive transportation modes with same label, into one

    Args:
        modes (:obj:`list` of :obj:`dict`)
    Returns:
        :obj:`list` of :obj:`dict`
    """
    if len(modes) > 0:
        previous = modes[0]
        grouped = []

        for changep in modes[1:]:
            if changep['label'] != previous['label']:
                previous['to'] = changep['from']
                grouped.append(previous)
                previous = changep

        previous['to'] = modes[-1]['to']
        grouped.append(previous)
        return grouped
    else:
        return modes

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
    changepoints = detect_changepoints(points, min_time)

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

    return group_modes(cp_info)
