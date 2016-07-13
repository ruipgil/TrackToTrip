import sys
import gpxpy
import gpxpy.gpx
import datetime
import argparse
import urllib2, zipfile, StringIO
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

def processFolderGroup(folder, output):
    # format: { walk: [ (start-time, end-time), ... ], ... }
    try:
        labels = readLabels(folder)

        trajFolder = join(folder, 'Trajectory')
        fileList = filter(lambda f: f.split('.')[-1] == 'plt', listdir(trajFolder))

        l = len(fileList)
        for i, f in enumerate(fileList):

            sys.stdout.write('Processing %d of %d: %s\r' % (i + 1, l, f))
            sys.stdout.flush()
            # format: [( label, segment ), ...]
            #       segment is : [ (lat, lon, time), ... ]
            segments = extractSegmentsFromFile(join(trajFolder, f), labels)
            if len(segments) > 0:
                saveSegments(segments, f, output)

        sys.stdout.write('Processed\n')
        sys.stdout.flush()
    except IOError:
        print('Skipping')
        return
    except KeyboardInterrupt:
        exit()
    except:
        print(sys.exc_info()[0])

def processDataset(root = 'Data', output = 'out'):
    folders = listdir(root)
    for folder in folders:
        f = join(root, folder)
        print('Going to ' + f)
        processFolderGroup(f, output)
    print('Done')

lastTime = None
def chunk_report(bytes_so_far, chunk_size, total_size):
   percent = float(bytes_so_far) / total_size
   percent = round(percent*100, 2)
   mb = 1024 * 1024
   sys.stdout.write("Downloaded %d of %dMB (%0.2f%%)\r" %
       (bytes_so_far / mb, total_size / mb, percent))

   if bytes_so_far >= total_size:
      sys.stdout.write('\n')

def chunk_read(response, chunk_size=8192, report_hook=None):
   total_size = response.info().getheader('Content-Length').strip()
   total_size = int(total_size)
   bytes_so_far = 0

   while 1:
      chunk = response.read(chunk_size)
      bytes_so_far += len(chunk)

      if not chunk:
         break

      if report_hook:
         report_hook(bytes_so_far, chunk_size, total_size)

   return bytes_so_far

def downloadDataset(toFolder):
    print('Dowloading GeoLife dataset from http://research.microsoft.com/en-us/downloads/b16d359d-d164-469e-9fd4-daa38f2b2e13/')
    print('This might take a few minutes, the file size is approximately 300MB')
    r = urllib2.urlopen('http://ftp.research.microsoft.com/downloads/b16d359d-d164-469e-9fd4-daa38f2b2e13/Geolife%20Trajectories%201.3.zip')
    chunk_read(r, report_hook=chunk_report)
    z = zipfile.ZipFile(StringIO.StringIO(r))
    z.extractall(toFolder)

parser = argparse.ArgumentParser(description='GeoLife Trajectory dataset transportation mode extractor.\n\nExtracts transportation mode from the dataset, into individual files,\nannotated with the following format:\n\t[transporation mode].[control].[nPoints].[original-file].gpx')
parser.add_argument('datasetFolder', metavar='datasetFolder', type=str, help='Path to the GeoLife dataset folder')
parser.add_argument('-o', '--output', metavar='outputFolder', type=str, help='Path to processed dataset')
parser.add_argument('-d', '--download', dest='download', action='store_true', required=False, help='Pass this flag to download the GeoLife dataset to the specified folder and to process it')
args = parser.parse_args()

print(args)
if args.download == True:
    downloadDataset(args.datasetFolder)
else:
    processDataset(args.datasetFolder, args.output)
