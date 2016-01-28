import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import numpy as np
import math

def dotProduct(one, two):
    return one.getLat()*two.getLat() + one.getLon()*two.getLon()

def dotProductP(one, two):
    return one*two

def dotProductOfArray(track, fn=dotProduct):
    dots = []
    for i in range(len(track)-1):
        point = track[i]
        nextp = track[i+1]
        dots.append(fn(point, nextp))
    return dots

def noiseFromSample(sample):
    return []

def noiseDetection(track):

    dots = dotProductOfArray(track)

    windowSize = 5
    noise = []
    for i in range(len(dots)-windowSize):
        sample = dots[i:(i+windowSize)]
        noise.extend(noiseFromSample(sample))

    plt.plot(dots)
    plt.show()

    """X = [ [v, track[i].getDt()] for i,v in enumerate(dots)]
    X = StandardScaler().fit_transform(X)
    db = DBSCAN(eps=0.5, min_samples=30).fit(X)
    labels = db.labels_

    maxDots = max(dots)
    colors = plt.cm.Spectral(np.linspace(0, 1, len(set(labels))))
    for i, label in enumerate(labels):
        color = 'k' if label == -1 else colors[label]
        plt.plot(i, dots[i], 'bo-', color=color, markeredgecolor=color)
    return plt"""

