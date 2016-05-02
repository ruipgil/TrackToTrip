import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import normalize

def normalizeSegments(segment):
    """
    Normalizes track points and returns the result as an array of 2D arrays
    """
    return normalize(map(lambda p: [p.lat, p.lon], segment))

def normalizeDots(dots):
    """
    Normalize numbers in an array
    """
    m = max(dots)
    return map(lambda d: d/m, dots)

def dot(points):
    """
    Calculates the dot product between every two vectors and returns an array with it
    :param points: Array of 2D arrays
    """
    return map(lambda i: np.dot(points[i], points[i+1]), range(len(points)-1))

def distance(arr):
    """
    Returns the distance between every two consecutive points in an array
    :param arr: Array of numbers
    """
    last = arr[0]
    result = []
    for elm in arr:
        result.append(abs(elm-last))
        last = elm
    return result

def plot(track, dots, noiseSet, average, variance):
    """
    Plot dot product of a track, alongside average and variance. Noise points
        are shown as dots

    Returns the matplotlib plot
    """
    # print(average, variance, average-variance, average+variance)

    plt.plot(dots)
    plt.plot([0, len(dots)], [average, average])
    plt.plot([0, len(dots)], [average-variance, average-variance])
    plt.plot([0, len(dots)], [average+variance, average+variance])
    for n in noiseSet:
        plt.plot(n, dots[n], 'o')

    return plt

def noiseDetection(segments, var=1):
    """
    Method to detect noise in the signal.

    The principal behind the detection is based on the changes in direction.
    Usually when there is noise in a GPS signal there will be points "very"
        distant and in different directions.
    We detect noise in the signal when those changes in direction are too
        abrupt, using the *dot product* between a point and the next one.
    The process is as follows:
        1. Normalize points
        2. Calculate the difference between two consecutive points, where
            the first is 0
        3. Normalize the differences
        4. Calculate the median and variance of the normalized differences
            and removing zero (stationary values)
        5. Values above *median + variance* are dropped

    The argument is a track: an array of points (Point).
    The return is an array with the indices of the points marked as noise
        relative to the argument.

    This approach doesn't take into consideration time intervals, just time
        sequence.
    """
    normalized = normalizeSegments(segments)

    dots = dot(normalized)
    dots = distance(dots)
    dots = normalizeDots(dots)

    dotsMapped = list(enumerate(dots))
    dotsMapped = filter(lambda dot: dot[1]!=0, dotsMapped)

    dotsForStats = map(lambda r: r[1], dotsMapped)
    average = np.median(dotsForStats)
    variance = np.var(dotsForStats) / var
    threshold = average + variance

    noise = []
    for i, d in dotsMapped:
        if d > threshold:
            noise.append(i)

    #plot(track, dots, noise, average, variance).show()
    return noise

def removeNoise(segment, var=2):
    noise = noiseDetection(segment, var=var)

    finalSet = set(range(len(segment))).difference(set(noise))
    noiselessSegment = []
    for i in finalSet:
        noiselessSegment.append(segment[i])
    return noiselessSegment
