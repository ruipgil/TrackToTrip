from tracktotrip import Track
import tracktotrip.transportation_mode as tm
from changepy import pelt
from changepy.costs import normal_mean

import numpy as np
import matplotlib.pyplot as plt

temp_trk = [
    Track.from_gpx('/Users/ruipgil/tracks/backup/2015-07-23_1.gpx')[0],
    Track.from_gpx('/Users/ruipgil/tracks/backup/2015-07-23_2.gpx')[0],
    Track.from_gpx('/Users/ruipgil/tracks/backup/2015-07-23_3.gpx')[0]
]

segs = []
for trke in temp_trk:
    segs.extend(trke.segments)
trk = Track("", segs)
trk.compute_metrics()
trk.to_trip('', 0, 5.0, 0.15, 80, 0.3, '%Y-%m-%d')

def raw_vel(seg):
    return [p.vel for p in seg.points]

def raw_acc(seg):
    return [p.acc for p in seg.points]

def abs_vel(seg):
    return [abs(p.vel) for p in seg.points]

def square_vel(seg):
    return [p.vel**2 for p in seg.points]

def diff_vel(seg):
    result = []
    last = None
    for p in seg.points:
        if last is None:
            result.append(0)
        else:
            result.append(last.vel-p.vel)
        last = p
    return result

def abs_diff_vel(seg):
    return [abs(v) for v in diff_vel(seg)]

def square_diff_vel(seg):
    return [v**3 for v in diff_vel(seg)]

def compute_metric(metric):
    return [metric(seg) for seg in trk.segments]

colors = 'rgby'
def plot(ax, data, changepoints):
    index = 0
    for i, seg_data in enumerate(data):
        ax.plot(range(index, len(seg_data) + index), seg_data, '-')
        for changepoint in changepoints[i]:
            ax.axvline(changepoint + index, color='k', linestyle='--')
        index = index + len(seg_data)

def pelt_(data):
    return pelt(normal_mean(data, np.std(data)), len(data))

plot_n = 1
plot_cols = 2
plot_rows = 3
def changepoint_for(metric):
    global plot_n

    ax = fig.add_subplot(plot_rows, plot_cols, plot_n)
    data = compute_metric(metric)
    changepoints = [pelt_(d) for d in data]

    ax.set_title("%s (%d changepoints)" % (metric.__name__, sum([len(c) for c in changepoints])))
    plot(ax, data, changepoints)

    plot_n = plot_n + 1

fig = plt.figure()
changepoint_for(raw_vel)
changepoint_for(abs_vel)
changepoint_for(square_vel)
changepoint_for(diff_vel)
changepoint_for(square_diff_vel)
changepoint_for(raw_acc)

plt.show()
