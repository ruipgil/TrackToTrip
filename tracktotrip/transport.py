import datetime
import math
import json
from os.path import isfile
from sklearn import tree

def t(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")

def calculateVelocity(dest, orig, d=True):
    if d==True:
        dd = math.sqrt((dest['lat']-orig['lat'])**2 + (dest['lon'] - orig['lon'])**2)
        dt = (t(dest['time']) - t(orig['time'])).total_seconds()
    else:
        dd = math.sqrt((dest.lat-orig.lat)**2 + (dest.lon - orig.lon)**2)
        dt = (dest.time - orig.time).total_seconds()
    if dt == 0:
        return 0

    return dd/dt

def buildFeaturesForTrack(track, d=True):
    m2 = None
    m1 = None
    num = len(track) - 2
    final = []
    for i in range(num):
        point = track[i]
        p1 = track[i+1]
        p2 = track[i+2]
        p1v = calculateVelocity(p1, point, d=d)
        p2v = calculateVelocity(p2, p1, d=d)

        data = None
        if m1 == None:
            data = [0, 0, p1v, p2v]
        elif m2 == None:
            m1v = calculateVelocity(m1, point, d=d)
            data = [0, m1v, p1v, p2v]
        else:
            m1v = calculateVelocity(m1, point, d=d)
            m2v = calculateVelocity(m2, m1, d=d)
            data = [m2v, m1v, p1v, p2v]
        m2 = m1
        m1 = point
        final.append(data)
    return final

def transport(track):
    if isfile("features.json"):
        # print("loading features")
        [X, Y] = json.loads(open("features.json","r").read())
    else:
        # print("building features")
        X, Y = buildTrainSet()
        saveToFile("features.json", [X, Y])

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X,Y)

    in_track = buildFeaturesForTrack(track, d=False)
    # print(in_track)
    result = clf.predict_proba(in_track)
    # print(result)
    return result

def saveToFile(name, obj):
    f = open(name, 'w')
    f.write(json.dumps(obj))
    f.close()

def buildTrainSet():
    train = [[], []]
    labels = ["airplane", "car", "bus", "subway", "taxi", "walk"]
    for label in labels:
        with open(label+'.json', 'r') as f:
            j = json.loads(f.read())
            for track in j:
                features = buildFeaturesForTrack(track)
                train[0].extend(features)
                train[1].extend(map(lambda f: label, features))
    return train[0], train[1]
