import gpxpy
from .preprocess import preprocess as preprocess
import numpy as np
import matplotlib.pyplot as plt


def loadGPX(name):
    return gpxpy.parse(open(name, 'r'))

def trackFromGPX(name):
    return preprocess(loadGPX(name))

def plotSegments(segments, annotate=False):
    colors = plt.cm.Spectral(np.linspace(0, 1, len(segments)))
    for s, segment in enumerate(segments):
        print(segment)
        print(len(segment))

        for i, point in enumerate(segment):
            y = point.getLat()
            x = point.getLon()
            if i==0:
                plt.plot(x, y, 'o', markersize=12, markerfacecolor=colors[s])
            elif len(segment)-1 == i:
                plt.plot(x, y, 'o', markersize=16, markerfacecolor=colors[s])
            else:
                plt.plot(x, y, 'o', markersize=6, markerfacecolor=colors[s])
            if annotate:
                plt.annotate(str(point.getId()) + " in " + str(i),
                        xy = (x, y), xytext = (-20, 20),
                        textcoords = 'offset points', ha = 'right', va = 'bottom',
                        bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
    return plt
