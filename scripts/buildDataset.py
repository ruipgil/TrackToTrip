import csv
import sys
from tracktotrip import Track
from os import listdir
from os.path import join
from sklearn import tree
# from sklearn import cross_validation
from sklearn.cross_validation import LabelKFold
from sklearn.cross_validation import train_test_split
"""
Outputs a C4.5 classifier that can be used by TrackToTrip
to identify transportation modes.
"""

def buildDataset(folder, output):
    dataset = {}
    files = listdir(folder)

    l = len(files)
    for i, f in enumerate(files):
        sys.stdout.write('Processing %d of %d: %s       \r' % (i+1, l, f))
        sys.stdout.flush()

        label = f.split('.')[0]
        # content = open(join(folder, f), 'r')
        track = Track.fromGPX(join(folder, f))[0]
        track.preprocess(destructive=False)
        # content.close()

        if not label in dataset:
            dataset[label] = []

        createFeatures(track, dataset, label)

    sys.stdout.write('\nExporting to CSV\n')
    sys.stdout.flush()
    with open(output, 'wb') as csvfile:
        w = csv.writer(csvfile, delimiter=' ')
        for label, features in dataset.iteritems():
            for feature in features:
                row = [label]
                row.extend(feature)
                w.writerow(row)

    print('\nDone')

    return dataset

def createFeatures(track, dataset, label):
    # Assumed that each track has one segment
    segment = track.segments[0]

    # this feature group is composed of (where i is the index):
    # [
    #   vel[i-5], ..., vel[i], ..., vel[i+5],
    #   acc[i-5], ..., acc[i], ..., acc[i+5]
    # ]

    window = 5
    nPoints = len(segment.points) - 1
    for i, point in enumerate(segment.points):
        pointFeatures = []
        for j in range(-window, window + 1):
            index = i + j
            vel = None
            acc = None
            if index > 0 and index <= nPoints:
                vel = segment.points[index].vel
                acc = segment.points[index].acc
            pointFeatures.append(vel)
            pointFeatures.append(acc)
        dataset[label].append(pointFeatures)

def loadDataset(filePath):
    with open(filePath, 'r') as f:
        labels = []
        data = []
        r = csv.reader(f, delimiter=' ')
        for row in r:
            label = row[0]
            d = row[1:]
            labels.append(label)
            data.append(d)

        labelSet = set(labels)
        labelMap = {}
        for i, ls in enumerate(labelSet):
            labelMap[ls] = i

        labels = map(lambda l: labelMap[l], labels)
        return {
                'data': data,
                'target': labels,
                'labels': labelSet
                }

def buildClassifier(dataset):
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(dataset.data, dataset.target)
    return clf

def plotClassifier(clf, dataset, name='clf'):
    with open("%s.dot" % name, 'w') as f:
        f = tree.export_graphviz(clf, out_file=f,
                         feature_names=dataset.feature_names,
                         class_names=dataset.target_names,
                         filled=True, rounded=True,
                         special_characters=True)

def crossValidate(clf, dataset):
    """Cross validate the classifier

    Uses k-fold method
    """
    X, y = dataset.data, dataset.target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    LabelKFold(dataset.labels, n_folds=4)
    return

def runDataset(dataset):
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(dataset['data'], dataset['target'])
    print(clf.predict([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]))
# Build dataset
# buildDataset('./dataset', './dataset.csv')
runDataset(loadDataset('./dataset.csv'))
