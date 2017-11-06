"""
MIT License
"""

import pickle
import numpy as np
from sklearn import preprocessing
from sklearn.linear_model import SGDClassifier

class Classifier(object):
    """ Transportation mode classifier

    This is a wrapper around sklearn SGDClassifier, to simplify it's usage

    Attributes:
        clf (:obj:`SGDClassifier`): Classifier being used
        labels (:obj:`LabelEncoder`): Label encoder, includes all the labels
        feature_length (int): Length of each feature. <0 if it hasn't learned any
    """
    def __init__(self, classifier=None):
        if classifier:
            self.clf = classifier
        else:
            self.clf = SGDClassifier(loss="log", penalty="l2", shuffle=True, n_iter=2500)
        self.labels = preprocessing.LabelEncoder()
        self.feature_length = -1

    def __learn_labels(self, labels):
        """ Learns new labels, this method is intended for internal use

        Args:
            labels (:obj:`list` of :obj:`str`): Labels to learn
        """
        if self.feature_length > 0:
            result = list(self.labels.classes_)
        else:
            result = []

        for label in labels:
            result.append(label)
        self.labels.fit(result)

    def learn(self, features, labels):
        """ Fits the classifier

        If it's state is empty, the classifier is fitted, if not
        the classifier is partially fitted.
        See sklearn's SGDClassifier fit and partial_fit methods.

        Args:
            features (:obj:`list` of :obj:`list` of :obj:`float`)
            labels (:obj:`list` of :obj:`str`): Labels for each set of features.
                New features are learnt.
        """
        labels = np.ravel(labels)
        self.__learn_labels(labels)
        if len(labels) == 0:
            return

        labels = self.labels.transform(labels)
        if self.feature_length > 0 and hasattr(self.clf, 'partial_fit'):
            # FIXME? check docs, may need to pass class=[...]
            self.clf = self.clf.partial_fit(features, labels)
        else:
            self.clf = self.clf.fit(features, labels)
            self.feature_length = len(features[0])

    def score(self, features, labels):
        labels = self.labels.transform(labels)
        return self.clf.score(features, labels)

    def predict(self, features, verbose=False):
        """ Probability estimates of each feature

        See sklearn's SGDClassifier predict and predict_proba methods.

        Args:
            features (:obj:`list` of :obj:`list` of :obj:`float`)
            verbose: Boolean, optional. If true returns an array where each
                element is a dictionary, where keys are labels and values are
                the respective probabilities. Defaults to False.
        Returns:
            Array of array of numbers, or array of dictionaries if verbose i
            True
        """
        probs = self.clf.predict_proba(features)
        if verbose:
            labels = self.labels.classes_
            res = []
            for prob in probs:
                vals = {}
                for i, val in enumerate(prob):
                    label = labels[i]
                    vals[label] = val
                res.append(vals)
            return res
        else:
            return probs

    def save_to_file(self, filename):
        """ Saves this instance to a file

        Args:
            filename (str)
        """
        pickle.dump(self, filename)

    @staticmethod
    def load_from_file(filename):
        """ Loads a classifier instance from a file

        Args:
            filename (str)
        """
        return pickle.load(filename)
