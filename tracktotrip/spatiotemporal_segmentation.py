"""
Spatio-temporal segmentation of points
"""
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def correct_segmentation(segments, clusters, min_time):
    """ Corrects the predicted segmentation

    This process prevents over segmentation

    Args:
        segments (:obj:`list` of :obj:`list` of :obj:`Point`):
            segments to correct
        min_time (int): minimum required time for segmentation
    """
    segments = [points for points in segments if len(points) > 1]

    result_segments = []
    prev_segment = None
    for i, segment in enumerate(segments):
        cluster = clusters[i]
        if prev_segment is None:
            prev_segment = segment
        else:
            cluster_dt = 0
            if len(cluster) > 0:
                cluster_dt = abs(cluster[0].time_difference(cluster[-1]))
            print(i, cluster_dt, cluster_dt <= min_time)
            if cluster_dt <= min_time:
                prev_segment.extend(segment)
            else:
                prev_segment.append(segment[0])
                result_segments.append(prev_segment)
                prev_segment = segment
    if prev_segment is not None:
        result_segments.append(prev_segment)

    return result_segments

def spatiotemporal_segmentation(points, eps, min_time):
    """ Splits a set of points into multiple sets of points based on
        spatio-temporal stays

    DBSCAN is used to predict possible segmentations,
        furthermore we check to see if each clusters is big enough in
        time (>=min_time). If that's the case than the segmentation is
        considered valid.

    When segmenting, the last point of the ith segment will be the same
        of the (i-1)th segment.

    Segments are identified through clusters.
    The last point of a clusters, that comes after a sub-segment A, will
        be present on the sub-segment A.

    Args:
        points (:obj:`list` of :obj:`Point`): segment's points
        eps (float): Epsilon to feed to the DBSCAN algorithm.
            Maximum distance between two samples, to be considered in
            the same cluster.
        min_time (float): Minimum time of a stay
    Returns:
        :obj:`list` of :obj:`list` of :obj:`Point`: Initial set of
            points in different segments
    """
    # min time / sample rate
    min_samples = min_time / np.average([point.dt for point in points])

    data = [point.gen3arr() for point in points]
    data = StandardScaler().fit_transform(data)
    db_cluster = DBSCAN(eps=eps, min_samples=min_samples).fit(data)
    labels = db_cluster.labels_

    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    segments = [[] for _ in range(n_clusters_+1)]
    clusters = [[] for _ in range(n_clusters_+1)]
    current_segment = 0

    # split segments identified with dbscan
    for i, label in enumerate(labels):
        if label != -1 and label + 1 != current_segment:
            current_segment = label + 1
        point = points[i]
        segments[current_segment].append(point)
        if label == -1:
            pass
        else:
            clusters[label + 1].append(point)

    return correct_segmentation(segments, clusters, min_time)
