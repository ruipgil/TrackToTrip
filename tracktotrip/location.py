"""
Location class and methods
"""
from math import sqrt
import requests
import numpy as np
from sklearn.cluster import DBSCAN
from .utils import estimate_meters_to_deg


GOOGLE_PLACES_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch' \
    '/json?location=%s,%s&radius=%s&key=%s'

def compute_centroid(points):
    """ Computes the centroid of set of points

    Args:
        points (:obj:`list` of [float, float])
    Returns:
        [float, float]: Latitude and longitude of the centroid
    """
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    return [np.mean(lats), np.mean(lons)]

def update_location_centroid(point, cluster, max_distance, min_samples):
    """ Updates the centroid of a location cluster with another point

    Args:
        point (:obj:`Point`): Point to add to the cluster
        cluster (:obj:`list` of :obj:`Point`): Location cluster
        max_distance (float): Max neighbour distance
        min_samples (int): Minimum number of samples
    Returns:
        ([float, float], :obj:`list` of :obj:`Point`): Tuple with the location centroid
            and new point cluster (given cluster + given point)
    """
    points = [p.gen2arr() for p in cluster]
    points.append(point.gen2arr())

    # Estimates the epsilon
    eps = estimate_meters_to_deg(sqrt(max_distance), precision=5)

    p_cluster = DBSCAN(eps=eps, min_samples=min_samples)
    p_cluster.fit(points)

    clusters = {}
    for i, label in enumerate(p_cluster.labels_):
        if label in clusters.keys():
            clusters[label].append(points[i])
        else:
            clusters[label] = [points[i]]

    centroids = []
    biggest_centroid_l = -float("inf")
    biggest_centroid = None

    for label, cluster in clusters.items():
        centroid = compute_centroid(cluster)
        centroids.append(centroid)

        if label >= 0 and len(cluster) >= biggest_centroid_l:
            biggest_centroid_l = len(cluster)
            biggest_centroid = centroid

    if biggest_centroid is None:
        biggest_centroid = compute_centroid(points)

    return biggest_centroid, points


def query_google(point, max_distance, key):
    """ Queries google maps API for a location

    Args:
        point (:obj:`Point`): Point location to query
        max_distance (float): Search radius, in meters
        key (str): Valid google maps api key
    Returns:
        :obj:`list` of :obj:`dict`: List of locations with the following format:
            {
                'label': 'Coffee house',
                'types': 'Commerce',
                'suggestion_type': 'GOOGLE'
            }
    """
    if not key:
        return []

    req = requests.get(GOOGLE_PLACES_URL % (
        point.lat,
        point.lon,
        max_distance,
        key
    ))

    if req.status_code != 200:
        return []
    response = req.json()
    results = response['results']
    # l = len(results)
    final_results = []
    for local in results:
        final_results.append({
            'label': local['name'],
            # 'rank': (l-i)/float(l),
            'types': local['types'],
            'suggestion_type': 'GOOGLE'
            })
    return final_results

def infer_location(point, location_query, max_distance, google_key, limit):
    """ Infers the semantic location of a (point) place.

    Args:
        points (:obj:`Point`): Point location to infer
        location_query: Function with signature, (:obj:`Point`, int) -> (str, :obj:`Point`, ...)
        max_distance (float): Max distance to a position, in meters
        google_key (str): Valid google maps api key
        limit (int): Results limit
    Returns:
        :obj:`Location`: with top match, and alternatives
    """
    locations = []

    if location_query is not None:
        queried_locations = location_query(point, max_distance)
        for (label, centroid, _) in queried_locations:
            locations.append({
                'label': label,
                'distance': centroid.distance(point),
                'cantroid': centroid,
                'suggestion_type': 'KB'
                })
        locations = sorted(locations, key=lambda d: d['distance'])

    if len(locations) <= limit:
        google_locs = query_google(point, max_distance, google_key)
        locations.extend(google_locs)

    locations = locations[:limit]

    return Location(locations[0]['label'], point, locations)


class Location(object):
    """ Location representation

    Params:
        label (str): Location name
        centroid (:obj:`Point`): Location position
        other (:obj:`list` of :obj:`dict`): Other possible locations. Includes the current label
    """
    def __init__(self, label, position, other):
        self.label = label
        self.centroid = position
        self.other = other

    def distance(self, position):
        """ Computes the distance between centroid and another point

        Args:
            position (:obj:`Point`)
        Returns:
            float: distance, in meters
        """
        return self.centroid.distance(position)

    def to_json(self):
        """ Converts to a json representation

        Returns:
            :obj:`dict`
        """
        return {
            'label': self.label,
            'position': self.centroid.to_json(),
            'other': self.other
        }

    @staticmethod
    def from_json(json):
        """ Converts from a json representation

        Returns:
            :obj:`Location`
        """
        return Location(json['label'], json['position'], [])
