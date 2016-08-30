import pickle
import time
import matplotlib.pyplot as plt
from tracktotrip.classifier import Classifier

_labels = pickle.load(open('geolife.3labels', 'r'))
_features = pickle.load(open('geolife.3features', 'r'))

def feat_morph(feats):
    return feats

alias = {
    'run': 'foot',
    'walk': 'foot',
    'bus': 'vehicle',
    'taxi': 'vehicle',
    'car': 'vehicle',
    'motorcycle': 'vehicle',
    'subway': 'train',
}
def label_alias(label):
    if label in alias.keys():
        return alias[label]
    return label

skips = ['bike', 'boat']

agl = {}
labels_count = {}
for i, label in enumerate(_labels):
    feature = feat_morph(_features[i])

    if label in labels_count.keys():
        labels_count[label] += 1
    else:
        labels_count[label] = 1

    if label in skips:
        continue

    label = label_alias(label)
    if label in agl.keys():
        agl[label].append(feature)
    else:
        agl[label] = [feature]


labels_details = []
for label, vals in agl.iteritems():
    aliased_from = ''
    if label in alias.values():
        aliased_from = []
        for original, als in alias.iteritems():
            if als == label:
                aliased_from.append('%s (%d samples)' % (original, labels_count[original]))
        aliased_from = ' aliased from: %s' % ', '.join(aliased_from)
    labels_details.append('%s (%d samples)%s' % (label, len(vals), aliased_from))
print 'Labels to use:\n  %s' % '\n  '.join(labels_details)
print ''
print 'Labels not used: %s' % ', '.join(['%s (%s samples)' % (label, labels_count[label]) for label in skips])


def split_agl(percentage):
    left = {}
    right = {}

    for label, features in agl.iteritems():
        index_left = int(len(features) * percentage)
        left[label] = features[:index_left]
        right[label] = features[index_left:]

    return left, right

train_set, test_set = split_agl(0.5)

def to_arrs(data):
    labels = []
    features = []
    for l, f in data.iteritems():
        for feature in f:
            labels.append([l])
            features.append(feature)
    return labels, features

a_labels, a_features = to_arrs(test_set)
b_labels, b_features = to_arrs(train_set)

from sklearn import tree
from sklearn.metrics import recall_score, f1_score, brier_score_loss, accuracy_score, coverage_error, mean_squared_error
from sklearn.metrics import classification_report
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import Perceptron, PassiveAggressiveClassifier
from sklearn.ensemble import GradientBoostingRegressor

def score(train_labels, train_features, test_labels, test_features, save_file, use_tree=False):
    if use_tree:
        train_clf = Classifier(tree.DecisionTreeClassifier())
    else:
        train_clf = Classifier()

    print train_clf.clf
    print ''

    t_start = time.clock()
    train_clf.learn(train_features, train_labels)
    t_end = time.clock()
    if save_file:
        train_clf.save_to_file(open(save_file, 'w'))

    p_start = time.clock()
    predicted = train_clf.clf.predict(test_features)
    p_end = time.clock()

    test_labels_t = train_clf.labels.transform(test_labels)
    print classification_report(test_labels_t, predicted, target_names=train_clf.labels.classes_)
    print 'Training time: %fs' % (t_end - t_start)
    print 'Predicting time: %fs' % (p_end - p_start)
    print 'Mean squared error: %f' % mean_squared_error(test_labels_t, predicted)
    return train_clf.score(test_features, test_labels)

def do_runs(n_runs, tree=False):
    result = []
    for i in range(n_runs):
        # print 'Run %s' % i
        print 'Split A (train: #%d, test: #%d)' % (len(a_labels), len(b_features))
        run_a = score(a_labels, a_features, b_labels, b_features, 'classifier.run_a.data', tree)
        print 'Score: %f' % run_a
        print ''
        print '-' * 40
        print ''
        print 'Split B (train: #%d, test: #%d)' % (len(b_labels), len(a_features))
        run_b = score(b_labels, b_features, a_labels, a_features, 'classifier.run_b.data', tree)
        print 'Score: %f' % run_b
        run_avrg = (run_a + run_b) / 2.0

        print ''
        print 'Average score was %f' % run_avrg
        result.append([run_a, run_b, run_avrg])

    return result

def plot_runs(runs):
    a_runs = [x[0] for x in runs]
    b_runs = [x[1] for x in runs]
    avrg_runs = [x[2] for x in runs]

    x = range(len(runs))
    plt.plot(x, a_runs, 'r')
    plt.plot(x, b_runs, 'b')
    plt.plot(x, avrg_runs, 'k--')

print ''
print '=' * 40
print ''
plot_runs(do_runs(1))
print '=' * 40
print ''
plot_runs(do_runs(1, True))
# plt.show()
