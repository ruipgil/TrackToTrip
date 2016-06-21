from sklearn import tree
import matplotlib.pyplot as plt
from .changepoint import changepoint
import numpy as np

CHANGE_TIME_THRESHOLD = 10 #60 seconds
def inferTransportationMode(points, method="Changepoint", removeStops=False, dt_threshold=CHANGE_TIME_THRESHOLD):
    if method == "Naive":
        tmodes = naiveTransportationInferring(points)
        tgroup = group(tmodes)
        result = []
        for j, (i, tm) in enumerate(tgroup):
            if len(tgroup) <= j + 1:
                end, _ = tgroup[j]
            else:
                end, _ = tgroup[j + 1]
            # if tm != 'Stop':
            result.append({
                'label': tm,
                'from': i,
                'to': end
                })
        return result
    elif method == "Changepoint":
        tmodes = speedClusteringTransportationInfering(points, dt_threshold=dt_threshold)
        if removeStops:
            return filter(lambda tm: tm['label'] != 'Stop', tmodes)
        else:
            return tmodes

def generateDatasetOn(arr, T=1, F=0, interpolate=1):
    N = 100
    X = []
    Y = []

    def fill(val, pb):
        # print(val, pb)
        samples = int(pb * N)
        counterSamples = N - samples
        for i in range(samples):
            X.append([val])
            Y.append(T)
        for i in range(counterSamples):
            X.append([val])
            Y.append(F)

    pastCls = None
    for cls in arr:
        val = cls['val']
        pb = cls['prob']
        fill(val, pb)
        if pastCls != None:
            IN = interpolate + 1
            iVal = (pastCls['val']-val)/IN
            iPb = (pastCls['prob']-pb)/IN
            for j in range(1, IN):
                fill((j * iVal) + val, (j * iPb) + pb)
        pastCls = cls
    return X, Y

def buildSoftClassifier(steps):
    X, Y = generateDatasetOn(steps, interpolate=100)
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X, Y)
    def getProb(val):
        return clf.predict_proba([[val]])[0][1]
    return getProb, clf

def plotSoftClassifier(clf, step, N=100):
    stp = step/N
    res = []
    for i in range(N):
        v = stp * i
        res.append([
            v, clf.predict_proba([[v]])
            ])
    plt.plot(map(lambda a: a[0], res), map(lambda a: a[1][0][1], res))
    return plt

stop, stopdt = buildSoftClassifier([{ 'val': 0, 'prob': 1 }, { 'val': 1, 'prob': 0.9 }, { 'val': 5, 'prob': 0.18 }, { 'val': 6.5, 'prob': 0 }])
walk, walkdt = buildSoftClassifier([{ 'val': 0, 'prob': 0 }, { 'val': 2, 'prob': 0.1 }, { 'val': 5, 'prob': 0.8 }, { 'val': 6.5, 'prob': 0.95 }, { 'val': 8, 'prob': 0.8 }, { 'val': 9, 'prob': 0.1 }, { 'val': 10, 'prob': 0 }])
run, rundt = buildSoftClassifier([{ 'val': 6.5, 'prob': 0 }, { 'val': 7, 'prob': 0.1 }, { 'val': 11, 'prob': 0.86 }, { 'val': 22, 'prob': 0.2 }, { 'val': 28, 'prob': 0 }])
bike, bikedt = buildSoftClassifier([{ 'val': 6.5, 'prob': 0 }, { 'val': 7, 'prob': 0.2 }, { 'val': 10, 'prob': 0.2 }, { 'val': 20, 'prob': 0.7 }, { 'val': 21, 'prob': 0.7 }, { 'val': 22, 'prob': 0.5 }, { 'val': 38, 'prob': 0 }])
vehicle, vehicledt = buildSoftClassifier([{ 'val': 9, 'prob': 0 }, { 'val': 10, 'prob': 0.05 }, { 'val': 20, 'prob': 0.05 }, { 'val': 38, 'prob': 0.9 }, { 'val': 40, 'prob': 1 }])

def softClassifySpeed(speed):
    return [
            stop(speed),
            walk(speed),
            # run(speed),
            # bike(speed),
            vehicle(speed)
            ]

def speedClusteringTransportationInfering(points, dt_threshold=CHANGE_TIME_THRESHOLD):
    vels = map(lambda p: p.vel, points)
    # get changepoint indexes
    cp = changepoint(vels)
    # insert last point to be a change point
    cp.append(len(points) - 1)

    # info for each changepoint
    cp_info = []

    for i in range(0, len(cp) - 1):
        fromIndex = cp[i]
        toIndex = cp[i+1]

        sp = np.mean(vels[fromIndex:toIndex])
        probs = softClassifySpeed(sp)
        cp_info.append({
            'from': fromIndex,
            'to': toIndex,
            'dt': points[toIndex].getTimestamp() - points[fromIndex].getTimestamp(),
            'average_speed': sp,
            'classification': probs,
            'label': choose_class(probs)
            })

    # group based on label
    previous = cp_info[0]
    grouped = []
    cum_dt = cp_info[0]['dt']

    for cp in cp_info[1:]:
        if cp['label'] != previous['label'] and cp['dt'] > dt_threshold:
            previous['to'] = cp['from']
            previous['dt'] = cum_dt
            grouped.append(previous)
            previous = cp
            cum_dt = 0
        cum_dt = cum_dt + cp['dt']
    previous['to'] = cp_info[-1]['to']
    grouped.append(previous)


    for g in grouped:
        print(g['label'], g['dt'], g['from'], g['to'])

    return grouped

def applyTransitionProbability(previous, current):
    transitions = {
            'Stop': [0.5, 0.5],
            'Vehicle': [0.5, 0.5]
            }

    tprob = transitions[previous['label']]
    newProb = current['classification'] * tprob
    current['classification'] = newProb
    current['label'] = choose_class(newProb)

    return current

def choose_class(elm):
    reprs = ['Stop',
            'Walk',
            # 'Run',
            # 'Bike',
            'Vehicle']
    return reprs[np.argmax(elm)]

def naiveTransportationInferring(points, S = 0.1, W = 7):
    """Infers the transportation mode of a set of points
    based on their velocity.

    The following association will be made between velocity
    and transportation modes:
    + 0 <= vel < S km/h : stationary
    + S <= vel < W km/h : on foot
    + W <= vel km/h     : on vehicle
    The default values for those transportation modes are:
    + S: 1 km/h
    + W: 5.5 km/h
    """

    tmodes = []
    for point in points:
        vel = point.vel
        if 0 <= vel and vel < S:
            tmodes.append('Stop')
        elif S <= vel and vel < W:
            tmodes.append('Foot')
        else:
            tmodes.append('Vehicle')

    return tmodes

def group(modes):
    last = None
    grp = []
    for i, mode in enumerate(modes):
        if last != mode:
            grp.append((i, mode))
            last = mode
    return grp
