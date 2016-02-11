import sys
import gpxpy
import gpxpy.gpx
import datetime
from os.path import join
from os import listdir

def ctime(day, hour="", sep="-"):
    t = day
    if len(hour) != 0:
        t += " " + hour
    return datetime.datetime.strptime(t, "%Y"+sep+"%m"+sep+"%d %H:%M:%S")

def readLabels(folder):
    labels = {}
    with open(join(folder, 'labels.txt'), 'r') as f:
        for line in f.readlines()[1:]:
            start, end, label = line.strip().split('\t')
            if not(label in labels):
                labels[label] = []
            start = ctime(start, sep="/")
            end = ctime(end, sep="/")
            labels[label].append((start, end))
    return labels

def readPlt(name):
    points = []
    with open(name, 'r') as f:
        for line in f.readlines()[6:]:
            lat, lon, _, alt, _, day, hour = line.strip().split(',')
            points.append({'lat': float(lat), 'lon': float(lon), 'alt': float(alt), 'time': ctime(day, hour)})
    return points

def extractSegmentsFromFile(f, labels):
    points = readPlt(f)
    _segments = {}
    table = []
    for label, segments in labels.iteritems():
        for segment in segments:
            table.append((label, segment[0], segment[1]))

    for point in points:
        ptime = point['time']
        for i, segment in enumerate(table):
            label, start, end = segment
            if start <= ptime and ptime <= end:
                if not(i in _segments):
                    _segments[i] = (label, [])
                _segments[i][1].append(point)
    return _segments.values()

def saveFile(folder, filename, content):
    name = join(folder, filename)
    with open(name, 'w') as f:
        f.write(content)
        f.close()

def saveSegments(segments, f, folder):
    name = f.split('/')[-1]
    for i, segment in enumerate(segments):
        label, points = segment
        filename = label + '.' + str(i) + '.' + str(len(points)) + '.' + name.split('.')[0] + '.gpx'

        gpx = gpxpy.gpx.GPX()

        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        for point in points:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(latitude=point['lat'], longitude=point['lon'], elevation=point['alt'], time=point['time']))

        saveFile(folder, filename, gpx.to_xml())

def processFolderGroup(folder):
    # format: { walk: [ (start-time, end-time), ... ], ... }
    labels = readLabels(folder)
    trajFolder = join(folder, 'Trajectory')
    fileList = filter(lambda f: f.split('.')[-1] == 'plt', listdir(trajFolder))
    for f in fileList:
        # format: [( label, segment ), ...]
        #       segment is : [ (lat, lon, time), ... ]
        segments = extractSegmentsFromFile(join(trajFolder, f), labels)
        if len(segments) > 0:
            saveSegments(segments, f, trajFolder)

def processDataset(root = 'Data'):
    folders = listdir(root)
    for folder in folders:
        f = join(root, folder)
        print('Going to ' + f)
        processFolderGroup(f)
    print('Done')

if len(sys.argv) >= 2:
    isHelp = filter(lambda e: e=='--h' or e=='-h' or e=='-help' or e=='--help', sys.argv)
    if len(isHelp)>0:
        print('GeoLife Trajectory dataset transportation mode extractor.\n\nExtracts transportation mode from the dataset, into individual files,\nannotated with the following format:\n\t[transporation mode].[control].[nPoints].[original-file].gpx\n\nUsage:\n\t' + sys.argv[0] + ' [folderToDataset]')
    else:
        processDataset(sys.argv[0])
else:
    processDataset()
