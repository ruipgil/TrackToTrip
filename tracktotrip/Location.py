import defaults
import requests
from sklearn.cluster import DBSCAN
import numpy as np


GOOGLE_PLACES_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch' \
    '/json?location=%s,%s&radius=%s&key=%s'

def computeCentroid(points):
    xs = map(lambda p: p[0], points)
    ys = map(lambda p: p[1], points)
    centroid = [np.mean(xs), np.mean(ys)]
    return centroid

def updateLocationCentroid(point, cluster, eps=0.00006, min_samples=2):
    X = map(lambda p: p.gen2arr(), cluster)
    X.append(point.gen2arr())

    km = DBSCAN(eps=eps, min_samples=min_samples)
    km.fit(X)

    clusters = {}
    for i in range(len(X)):
        label = km.labels_[i]
        if label in clusters.keys():
            clusters[label].append(X[i])
        else:
            clusters[label] = [X[i]]

    centroids = []
    biggest_centroid_l = -float("inf")
    biggestCentroid=None

    for label, cluster in clusters.items():
        centroid = computeCentroid(cluster)
        centroids.append(centroid)

        if label >= 0 and len(cluster) >= biggest_centroid_l:
            biggest_centroid_l = len(cluster)
            biggestCentroid = centroid

    if biggestCentroid is None:
        biggestCentroid = computeCentroid(X)

    return biggestCentroid, X


def query_google(point, max_distance, key):
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
    return map(lambda (i, r): {
        'label': r['name'],
        # 'rank': (l-i)/float(l),
        # 'vinicity': r['vinicity'] if 'vicinity' in r else '',
        'types': r['types'],
        'suggestion_type': 'GOOGLE'}, enumerate(results))


def inferLocation(
    point,
    location_query,
    max_distance=defaults.LOCATION_MAX_DISTANCE,
    google_key='',
    limit=defaults.LOCATIONS_LIMIT
):

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


class Location:
    def __init__(self, label, position, other=[]):
        self.label = label
        self.centroid = position
        self.other = other

    def distance(self, position):
        return self.centroid.distance(position)

    def toJSON(self):
        return {
            'label': self.label,
            'position': self.centroid.toJSON(),
            'other': self.other
        }

    @staticmethod
    def fromJSON(json):
        return Location(json['label'], json['position'])
