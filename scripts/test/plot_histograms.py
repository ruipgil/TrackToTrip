import math
import pickle
import numpy as np
import matplotlib.pyplot as plt
from tracktotrip.transportation_mode import extract_features_2

histograms = pickle.load(open('geolife.histogram', 'r'))
labels = pickle.load(open('geolife.histogram_labels', 'r'))

def cum_prob(histogram, steps):
    steps = sorted(steps)
    step_i = 0
    prob = 0.0
    result = []
    for i, val in enumerate(histogram):
        prob = prob + val
        while True:
            if prob > steps[step_i]:
                step_i = step_i + 1
                result.append(i)
                if len(result) == len(steps):
                    return result
            else:
                break
    return result

def normalize(histogram):
    total = float(sum(histogram))
    if total == 0:
        return [0]
    return [x / total for x in histogram]

def average(histograms):
    final = [0.0] * 10
    for histogram in histograms:
        for j, val in enumerate(histogram):
            if j >= len(final):
                final.extend([0.0] * (j - len(final) + 1))
            final[j] += val
    return normalize(final)


def plot(cumulative):
    ttl = 'Cumulative histogram' if cumulative else 'Histogram'
    histo_labels = {}
    for i, histogram in enumerate(histograms):
        label = labels[i]
        n_histogram = normalize(histogram)
        if len(n_histogram) > 1 and label in histo_labels:
            histo_labels[label].append(n_histogram)
        else:
            histo_labels[label] = [n_histogram]

    fig = plt.figure(figsize=(10, 40))
    n_splots = len(histo_labels.keys())

    i = 1
    for label, histogram in histo_labels.iteritems():
        ax = fig.add_subplot(n_splots, 1, i)
        i = i + 1
        hst = average(histogram)
        # plt.plot(range(len(hst)), hst, label=label)
        # ax.hist(range(len(hst)), len(hst), weights=hst, label=label)
        ax.hist(range(len(hst)), len(hst), weights=hst, cumulative=cumulative, edgecolor='none', range=(0, 400))
        ax.set_ylim([0, 1])
        ax.set_xlim([0, 400])
        print(label, cum_prob(hst, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]))
        ax.set_title('%s for %s' % (ttl, label.capitalize()))
    # plt.legend()
    plt.tight_layout()
    plt.savefig('cum_histograms.pdf' if cumulative else 'histogram.pdf')

plot(False)
plot(True)

