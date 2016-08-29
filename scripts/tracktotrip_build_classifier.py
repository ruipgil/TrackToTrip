#!/bin/env python
"""
Builds a classifier
"""
import sys
import pickle
import argparse
from os import listdir
from os.path import join, expanduser

from tracktotrip import Track
from tracktotrip.classifier import Classifier
from tracktotrip.transportation_mode import extract_features_2

def process_track(filename):
    """ Processes a file track, extracting it's features

    Args:
        filename
    Returns:
        list of float
    """
    track = Track.from_gpx(filename)[0]
    track.compute_metrics()

    for segment in track.segments:
        features = extract_features_2(segment.points)
    return features

def process_folder(folder, alias=None, skip=None):
    """ Processes a folder

    Uses files that follow the format: <label>.(<...>.)gpx

    Args:
        folder (str)
        alias (dict): optional, alias mappings
        skip (set): optional, labels to skip
    Returns:
        (list of str, list of list of float): labels, features tuple
    """
    if skip is None:
        skip = set()
    if alias is None:
        alias = {}
    files = listdir(folder)
    files = [f for f in files if f.endswith('.gpx')]

    labels = []
    features = []
    alias_keys = list(alias.keys())
    n_files = len(files)
    for i, gpx in enumerate(files):
        sys.stdout.write('Processing %d of %d: %s\r' % (i + 1, n_files, gpx))
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

def build_classifier(dataset_folder, destination_folder, features=None, labels=None):
    """ Entry function
    """

    if features is None and labels is None:
        labels = open(expanduser(labels), 'r')
        features = open(expanduser(features), 'r')
    else:
        features, labels = process_folder(expanduser(dataset_folder))

        print 'Saving features and labels'
        pickle.dump(features, open('geolife.features', 'w'))
        pickle.dump(labels, open('geolife.labels', 'w'))

    print 'Training classifier'
    clf = Classifier()
    clf.learn(features, labels)

    classifier_path = join(expanduser(destination_folder), 'classifier.data')
    print 'Saving classifier to %s' % classifier_path
    with open(classifier_path, 'w') as cls_file:
        clf.save_to_file(cls_file)

PARSER = argparse.ArgumentParser()
PARSER.add_argument(
    'datasetFolder',
    metavar='datasetFolder',
    type=str,
    help='Path to the dataset, such as the GeoLife dataset'
)
PARSER.add_argument(
    '-o',
    '--output',
    metavar='outputFolder',
    type=str,
    help='Folder to store the classifier'
)
PARSER.add_argument(
    '-f',
    '--features',
    metavar='features',
    type=str,
    help='Path to features file to use'
)
PARSER.add_argument(
    '-l',
    '--labels',
    metavar='labels',
    type=str,
    help='Path to features file to use'
)
ARGS = PARSER.parse_args()

build_classifier(ARGS.datasetFolder, ARGS.outputFolder, features=ARGS.features, labels=ARGS.labels)
