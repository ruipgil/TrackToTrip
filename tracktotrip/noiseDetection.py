import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import numpy as np
import math
from sklearn.preprocessing import normalize
from scipy import stats

def normalizeTrack(track):
    return normalize(map(lambda p: [p.getLat(), p.getLon()], track))

def dot(points):
    return map(lambda i: np.dot(points[i], points[i+1]), range(len(points)-1))

def distance(arr):
    last = arr[0]
    result = []
    for elm in arr:
        result.append(abs(elm-last))
        last = elm
    return result

def strategy(sample, av, var):
    threshold = av+var
    result = []
    for i, s in enumerate(sample):
        if s > threshold:
            result.append(i)
    return result

def noiseDetection(track):
    normalized = normalizeTrack(track)
    dots = dot(normalized)
    dots = distance(dots)
    m = max(dots)
    dots = map(lambda d: d/m, dots)
    dotsMapped = list(enumerate(dots))
    dotsMapped = filter(lambda dot: dot[1]!=0, dotsMapped)
    dotsForStats = map(lambda r: r[1], dotsMapped)

    average = np.median(dotsForStats)
    variance = np.var(dotsForStats)

    WINDOW = 10
    SLIDE = 1

    noise = []
    for i in range(len(dotsMapped)-WINDOW):
        index = i
        start = index
        end = index+WINDOW
        sample = dotsMapped[start:end]
        noises = strategy4(map(lambda d: d[1], sample), average, variance)
        for n in noises:
            noise.append(sample[n][0])

    noise = set(noise)

    plt.plot(dots)
    print(average, variance, average-variance, average+variance)
    plt.plot([0, len(dots)], [average, average])
    plt.plot([0, len(dots)], [average-variance, average-variance])
    plt.plot([0, len(dots)], [average+variance, average+variance])
    for n in noise:
        plt.plot(n, dots[n], 'o')
    plt.show()
    return noise

