import pandas
import numpy as np

def changepoint(data):
    s = pandas.Series(data)
    s = s.pct_change()
    s = s.fillna(value=0)
    s = s.abs()

    stat_s = []
    inf = float('inf')
    changepoints = []
    for i, v in enumerate(s):
        if v == inf:
            changepoints.append(i)
            stat_s.append(0)
        else:
            stat_s.append(v)

    var = np.var(stat_s)
    mean = np.mean(stat_s)
    print(mean, var)

    up_threshold = mean + var
    for i, d in enumerate(s):
        if d >= up_threshold:
            changepoints.append(i)

    changepoints = list(set(changepoints))
    changepoints.sort()

    return map(lambda cp: cp-1, changepoints)

def changePointSegmentation(mapper, data):
    X = changepoint(map(mapper, data))
    segments = []
    for i in range(0, len(X)-1):
        segments.append(data[X[i]:X[i+1]])

    return segments

