#!/bin/env python
"""
GeoLife dataset downloader and extractor
"""
import sys
import datetime
import urllib2
import zipfile
import argparse
import StringIO
from os import listdir
from os.path import join
import gpxpy
import gpxpy.gpx

def ctime(day, hour="", sep="-"):
    """ Creates a datetime object from a string

    Args:
        day (str)
        hour (str)
        sep (str): optional, hours separator. Defaults to "-"
    """
    if len(hour) != 0:
        day += " " + hour
    return datetime.datetime.strptime(day, "%Y"+sep+"%m"+sep+"%d %H:%M:%S")

def read_labels(folder):
    """ Reads labels from the labels.txt in the specified folder

    Args:
        folder (str)
    Returns:
        dict: Such as: {
            'walk': [(<datetime.datetime>, <datetime.datetime>), ...],
            ...
        }
    """
    labels = {}
    with open(join(folder, 'labels.txt'), 'r') as labels_file:
        for line in labels_file.readlines()[1:]:
            start, end, label = line.strip().split('\t')
            if not label in labels:
                labels[label] = []
            start = ctime(start, sep="/")
            end = ctime(end, sep="/")
            labels[label].append((start, end))
    return labels

def read_plt(name):
    """ Reads a plt file

    Args:
        name (str): file name
    Returns:
        list of dict: List with point, like [{
            'lat': 23.434,
            'lon': -21.9348,
            'alt': 21.12,
            'time': <datetime.datetime>
        }, ...]
    """
    points = []
    with open(name, 'r') as plt_file:
        for line in plt_file.readlines()[6:]:
            lat, lon, _, alt, _, day, hour = line.strip().split(',')
            points.append({
                'lat': float(lat),
                'lon': float(lon),
                'alt': float(alt),
                'time': ctime(day, hour)
            })
    return points

def extract_segments_from_file(plt_file, labels):
    """ Extracts segments and transportation modes from a plt file
    """
    points = read_plt(plt_file)
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
                if not i in _segments:
                    _segments[i] = (label, [])
                _segments[i][1].append(point)
    return _segments.values()

def save_file(folder, filename, content):
    """ Saves content to file
    """
    name = join(folder, filename)
    with open(name, 'w') as dest_file:
        dest_file.write(content)
        dest_file.close()

def save_segments(segments, origina_filepath, folder):
    """ Save segments to gpx
    """
    name = origina_filepath.split('/')[-1]
    for i, segment in enumerate(segments):
        label, points = segment
        filename = label + '.' + str(i) + '.' + str(len(points)) + '.' + name.split('.')[0] + '.gpx'

        gpx = gpxpy.gpx.GPX()

        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        for point in points:
            gpx_point = gpxpy.gpx.GPXTrackPoint(
                latitude=point['lat'],
                longitude=point['lon'],
                elevation=point['alt'],
                time=point['time']
            )
            gpx_segment.points.append(gpx_point)

        save_file(folder, filename, gpx.to_xml())

def process_folder_group(folder, output):
    """ Processes a folder that contains .plt files

    Args:
        folder (str): input folder
        output (str): output folder
    """
    # format: { walk: [ (start-time, end-time), ... ], ... }
    try:
        labels = read_labels(folder)

        traj_folder = join(folder, 'Trajectory')
        file_list = [f.split('.')[-1] == 'plt' for f in listdir(traj_folder)]

        n_files = len(file_list)
        for i, plt_file in enumerate(file_list):
            sys.stdout.write('Processing %d of %d: %s\r' % (i + 1, n_files, plt_file))
            sys.stdout.flush()
            # format: [( label, segment ), ...]
            #       segment is : [ (lat, lon, time), ... ]
            segments = extract_segments_from_file(join(traj_folder, plt_file), labels)
            if len(segments) > 0:
                save_segments(segments, plt_file, output)

        sys.stdout.write('Processed\n')
        sys.stdout.flush()
    except IOError:
        print 'Skipping'
    except KeyboardInterrupt:
        exit()
    except:
        print sys.exc_info()[0]

def process_dataset(root='Data', output='out'):
    """ Convert GeoLife plt files to gpx files. Expects GeoLife original folder structure.

    Args:
        root (str)
        output (str)
    """
    folders = listdir(root)
    for folder in folders:
        folder = join(root, folder)
        print 'Going to ' + folder
        process_folder_group(folder, output)
    print 'Done'

def chunk_report(bytes_so_far, _, total_size):
    """ Reports chucks received
    """
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    one_mb = 1024 * 1024
    sys.stdout.write("Downloaded %d of %dMB (%0.2f%%)\r" %
                     (bytes_so_far / one_mb, total_size / one_mb, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')

def chunk_read(response, chunk_size=8192, report_hook=None):
    """ Chunks read
    """
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

DATASET_URL = "http://research.microsoft.com/en-us/downloads/b16d359d-d164-469e-9fd4-daa38f2b2e13/"
DATASET_FILE = "%s.Geolife%%20Trajectories%%201.3.zip" % DATASET_URL
def download_dataset(to_folder):
    """ Downloads and extracts dataset to folder

    Args:
        to_folder (str): destination folder
    """
    print "Dowloading GeoLife dataset from %s" % DATASET_URL
    print "This might take a few minutes, the file size is approximately 300MB"
    reader = urllib2.urlopen(DATASET_FILE)
    chunk_read(reader, report_hook=chunk_report)
    zipf = zipfile.ZipFile(StringIO.StringIO(reader))
    print 'Extracting to %s' % to_folder
    zipf.extractall(to_folder)
    print 'Extracted'

PARSER = argparse.ArgumentParser(description="""\
GeoLife Trajectory dataset transportation mode extractor.

Extracts transportation mode from the dataset, into individual files,
annotated with the following format:
    [transporation mode].[control].[nPoints].[original file name].gpx
""")
PARSER.add_argument(
    'datasetFolder',
    metavar='datasetFolder',
    type=str,
    help='Path to the GeoLife dataset folder'
)
PARSER.add_argument(
    '-o',
    '--output',
    metavar='outputFolder',
    type=str,
    help='Path to processed dataset'
)
PARSER.add_argument(
    '-d',
    '--download',
    dest='download',
    action='store_true',
    required=False,
    help='Pass this flag to download the GeoLife dataset to the specified folder and to process it'
)
ARGS = PARSER.parse_args()

if ARGS.download:
    download_dataset(ARGS.datasetFolder)
if ARGS.outputFolder:
    process_dataset(ARGS.datasetFolder, ARGS.output)
