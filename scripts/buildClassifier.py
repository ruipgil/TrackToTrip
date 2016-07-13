import sys
from os import listdir
from os.path import join
import numpy as np
from tracktotrip.Track import Track
from tracktotrip.classifier import Classifier
import pickle

def process_track(filename):
    t = Track.fromGPX(filename)[0]
    t.compute_metrics()

    for segment in t.segments:
        features = extract_features(segment.points)
    return features

MAX = 300

def extract_features(points, ns=4):
    # inits histogram
    histogram = [0] * MAX
    # fills histogram
    for point in points:
        bin_index = int(round(point.vel))
        histogram[bin_index] += point.dt

    time = sum(histogram)
    result = []

    if time == 0:
        return result

    for _ in range(ns):
        max_index = np.argmax(histogram)
        value = histogram[max_index] / time
        result.extend([max_index, value])
        histogram[max_index] = -1

    return result

def process_folder(folder):
    files = listdir(folder)
    files = filter(lambda f: f.endswith('.gpx'), files)

    labels = []
    features = []
    l = len(files)
    for i, gpx in enumerate(files):
        sys.stdout.write('Processing %d of %d: %s\r' % (i + 1, l, gpx))
        sys.stdout.flush()

        try:
            label = gpx.split('.')[0]
            feature = process_track(join(folder, gpx))

            if len(feature) > 0:
                labels.append(label)
                features.append(feature)
        except:
            pass

    return features, labels

features, labels = process_folder('./dataset')

print('Saving features and labels')
pickle.dump(features, open('geolife.features', 'w'))
pickle.dump(labels, open('geolife.labels', 'w'))

print('Classifier built')
clf = Classifier()
clf.learn(features, labels)

