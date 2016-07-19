"""
Changepoint function
"""
import pandas
import numpy as np

def changepoint(data, min_time):
    """ Calculates a change point

    Args:
        data (:obj:`list` of float)
        min_time (float): Min time, in seconds, until another changepoint
    Returns:
        :obj:`list` of int: Changepoints indexes
    """
    series = pandas.Series(data)
    series = series.pct_change()
    series = series.fillna(value=0)
    series = series.abs()

    stat_series = []
    inf = float('inf')
    changepoints = []
    for i, val in enumerate(series):
        if val == inf:
            changepoints.append(i)
            stat_series.append(0)
        else:
            stat_series.append(val)

    var = np.var(stat_series)
    mean = np.mean(stat_series)

    up_threshold = mean + var * 2
    for i, vel in enumerate(series):
        if vel >= up_threshold:
            changepoints.append(i)

    changepoints = list(set(changepoints))
    changepoints.sort()

    return [cp-1 for cp in changepoints]
