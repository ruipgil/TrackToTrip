#!/bin/env python
"""
Provides gpx track manipulation
"""
import math
import argparse
from random import uniform, seed
from os.path import join, expanduser
from datetime import timedelta
from tracktotrip import Point, Track

ANONYMIZE = 1
ORGANIZE = 3
SPLIT = 2

PARSER = argparse.ArgumentParser(description='Manipulate tracks')
PARSER.add_argument(
    '-a',
    '--anonymize',
    dest='action',
    action='store_const',
    const=ANONYMIZE,
    help='anonymizes tracks, by doing random rotations and translations'
)
PARSER.add_argument(
    '-s',
    '--split',
    dest='action',
    action='store_const',
    const=SPLIT,
    help='splits tracks so that each file contains a segment'
)
PARSER.add_argument(
    '-o',
    '--organize',
    dest='action',
    action='store_const',
    const=ORGANIZE,
    help='takes all tracks and split them, naming them according with their start date'
)
PARSER.add_argument(
    '--eps', default=1.0, help='max distance to other points. Used when spliting. Defaults to 1.0'
)
PARSER.add_argument(
    '--mintime', default=120, help='minimum time required to split, in seconds. Defaults to 120'
)
PARSER.add_argument(
    '--seed', help='random number generator seed. Used when anonymizing'
)
PARSER.add_argument(
    'track',
    help='track to process, must be a gpx file',
    nargs='+'
)
PARSER.add_argument(
    'output_folder'
)
ARGS = PARSER.parse_args()

def translate(track, trans):
    """ Inplace translation of every point of a track by the same amount

    Args:
        track (:obj:`Track`)
        trans (:obj:`Point`): Amout to translate
    """
    print '\ttranslating by (%f, %f)' % (trans.lat, trans.lon)
    for segment in track.segments:
        for point in segment.points:
            point.lat += trans.lat
            point.lon += trans.lon

def rotate(track, degrees):
    """ Inplace rotation of every point of a track

    Args:
        track (:obj:`Track`)
        trans (float): Angle, in degrees
    """
    print '\trotating by %f degrees' % degrees
    theta = math.radians(degrees)
    for segment in track.segments:
        for point in segment.points:
            lat = point.lat * math.cos(theta) - point.lon * math.sin(theta)
            lon = point.lat * math.sin(theta) + point.lon * math.cos(theta)
            point.lat = lat
            point.lon = lon

def move_time(track, interval):
    """ Inplace time shift of a track

    Args:
        track (:obj:`Track`)
        trans (:obj:`timedelta`): Time delta to shift
    """
    print '\tmoving time by %s' % interval
    for segment in track.segments:
        for point in segment.points:
            point.time = point.time + interval

def anonymize(src):
    """ Anonymizes a (gpx) track

    Args:
        src (str): File path of the track to anonymize
    """
    track = Track.from_gpx(src)[0]
    if ARGS.seed:
        seed(ARGS.seed)

    point_index = int(uniform(0, len(track.segments[0].points)))
    print '\tselected point with index %d to use' % point_index
    # translate to the center
    start_point = track.segments[0].points[point_index]
    translate(track, Point(-start_point.lat, -start_point.lon, None))
    # rotate
    rotate(track, uniform(.0, 365.0))
    # randomize time
    move_time(track, timedelta(days=uniform(-3000.0, 3000.0)))

    dest_path = join(expanduser(ARGS.output_folder), 'anonymous_%s' % track.name)
    with open(dest_path, 'w') as fle:
        print '\t! saving to "%s"' % dest_path
        fle.write(track.to_gpx())

def split(src):
    """ Splits all track segments into individual gpx files

    Args:
        src (str): File path of the track to anonymize
    """
    track = Track.from_gpx(src)[0]
    track.compute_metrics()
    track.segment(ARGS.eps, ARGS.mintime)

    for i, segment in enumerate(track.segments):
        name = u'%s_%d.gpx' % (track.name.split('.')[0], i)
        trk = Track(name, [segment])

        dest_path = join(expanduser(ARGS.output_folder), '%s' % trk.name)
        with open(dest_path, 'w') as fle:
            print '\t! saving to "%s"' % dest_path
            fle.write(trk.to_gpx())

def organize_by_days(srcs):
    """ Organizes tracks by days. An numbers them in occurrence order.

    Args:
        srcs (list of str): Source paths of tracks
    """
    print 'Organizing'
    days = {}
    for src in srcs:
        print '\tinspecting %s' % src
        track = Track.from_gpx(src)[0]
        track.compute_metrics()
        track.segment(ARGS.eps, ARGS.mintime)

        for segment in track.segments:
            day = segment.points[0].time.date().isoformat()
            if day in days.keys():
                days[day].append(segment)
            else:
                days[day] = [segment]

    print 'Sorting and saving by days'
    for day, segments in days.iteritems():
        segments = sorted(segments, key=lambda segment: segment.points[0].time)
        for i, segment in enumerate(segments):
            name = u'%s_%d.gpx' % (day, i)
            trk = Track(name, [segment])

            dest_path = join(expanduser(ARGS.output_folder), '%s' % trk.name)
            with open(dest_path, 'w') as fle:
                print '\t! saving to "%s"' % dest_path
                fle.write(trk.to_gpx())


def main():
    """ Dispatches actions
    """
    if ARGS.action is ANONYMIZE:
        for src in ARGS.track:
            print 'Anonymizing %s' % src
            anonymize(src)
    elif ARGS.action is SPLIT:
        for src in ARGS.track:
            print 'Spliting %s' % src
            split(src)
    elif ARGS.action is ORGANIZE:
        organize_by_days(ARGS.track)
    else:
        print 'Provide one of the following actions:\n  organize\n  anonymize\n  split\nUse the --help flag for more information'

main()
