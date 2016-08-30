#!/bin/env python
"""
Build a histogram for a processed geolife dataset
"""
import sys
import pickle
import argparse
from os import listdir
from os.path import join, userexpand
from tracktotrip import Track

def extract_features(points):
    max_bin = -1
    for point in points:
        max_bin = max(max_bin, point.vel)
    max_bin = int(round(max_bin)) + 1

    # inits histogram
    histogram = [0.0] * max_bin
    time = 0

    # fills histogram
    for point in points:
        bin_index = int(round(point.vel))
        histogram[bin_index] += point.dt
        time += point.dt

    return histogram


def process_track(filename):
    t = Track.from_gpx(filename)[0]
    t.compute_metrics()

    for segment in t.segments:
        features = extract_features(segment.points)
    return features

def process_folder(folder, alias={}, skip=[]):
    files = listdir(folder)
    files = [f for f in files if f.endswith('.gpx')]

    labels = []
    features = []
    alias_keys = list(alias.keys())
    l = len(files)
    for i, gpx in enumerate(files):
        sys.stdout.write('Processing %d of %d: %s\r' % (i + 1, l, gpx))
        sys.stdout.flush()

        label = gpx.split('.')[0]
        label = label.lower()
        if label in skip:
            continue

        if label in alias_keys:
            label = alias[label]

        feature = process_track(join(folder, gpx))

        if len(feature) > 0:
            labels.append(label)
            features.append(feature)

    return features, labels

def main(dataset_folder, output_folder):
    features, labels = process_folder(userexpand(dataset_folder))
    print 'Saving features and labels'
    pickle.dump(features, open(join(userexpand(output_folder), 'geolife.histogram'), 'w'))
    pickle.dump(labels, open(join(userexpand(output_folder), 'geolife.histogram_labels'), 'w'))

PARSER = argparse.ArgumentParser(description='Manipulate tracks')
PARSER.add_argument(
    '-o',
    '--output',
    dest='output',
    default='.',
    help='output folder to place geolife.histogram and geolife.histogram_labels'
)
PARSER.add_argument(
    'dataset_folder',
    help='path to the PROCESSED GeoLife dataset folder'
)
ARGS = PARSER.parse_args()

main(ARGS.dataset_folder, ARGS.output)
