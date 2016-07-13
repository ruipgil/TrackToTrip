from tracktotrip.classifier import Classifier
import pickle

features = pickle.load(open('geolife.features', 'r'))
labels = pickle.load(open('geolife.labels', 'r'))

print('Classifier built')
clf = Classifier()
clf.learn(features, labels)
clf.save_to_file(open('classifier.data', 'w'))

# print(clf.predict([0, 0.7, 0, 0.2, ]))
# print(clf.predict([1, 0.7]))

# from sklearn.cross_validation import KFold
#
# kf = KFold(4, n_folds=2)
# for train_index, test_index in kf:
#     X_train, X_test = X[train_index], X[test_index]
#     y_train, y_test = y[train_index], y[test_index]
#
# scores = cross_validation.cross_val_score(
#     clf,
#     iris.data,
#     iris.target,
#     cv=5,
#     scoring='f1_weighted'
# )

