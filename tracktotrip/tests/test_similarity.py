from tracktotrip.segmentSimilarity import line, angle_similarity, distanceToLine, distance_similarity, normalize, lineDistance_similarity, line_similarity, sortSegmentPoints, segment_similarity
import unittest
import math
import matplotlib.pyplot as plt
from tracktotrip import Segment, Track, Point, kalman

class TestSimilarity(unittest.TestCase):
    def test_angle__similarity(self):
        l1p1 = [10, 10]
        l1p2 = [10, 12]
        l1 = line(l1p1, l1p2)

        l2p1 = [11, 10]
        l2p2 = [10, 10]
        l2 = line(l2p1, l2p2)

        self.assertEqual(angle_similarity(normalize(l1), normalize(l2)), 0)
        self.assertEqual(angle_similarity(normalize([0, 1]), normalize([1, 1])), angle_similarity(normalize([1, 0]), normalize([1, 1])))
        self.assertEqual(angle_similarity(normalize([0, 1]), normalize([0, -1])), -1)

    def test_distance(self):
        sqrt2 = math.sqrt(2)
        self.assertEqual(distanceToLine([0,0], [4,2], [0,0]), 0)
        self.assertEqual(distanceToLine([0,0], [4,2], [4,2]), 0)
        self.assertEqual(distanceToLine([0,0], [4,2], [2,1]), 0)
        self.assertEqual(distanceToLine([0,0], [2,2], [0,2]), sqrt2)
        self.assertEqual(distanceToLine([0,0], [2,2], [3,3]), sqrt2)

    def test_distance__similarity(self):
        self.assertEqual(distance_similarity([0,0], [4,2], [0,0], T=1), 1)
        self.assertEqual(distance_similarity([0,0], [4,2], [4,2], T=1), 1)
        self.assertEqual(distance_similarity([0,0], [4,2], [2,1], T=1), 1)

        self.assertEqual(distance_similarity([0,0], [2,0], [0,1], T=1), 0)
        self.assertEqual(distance_similarity([0,0], [2,0], [0,0.5], T=1), 0.5)
        self.assertEqual(distance_similarity([0,0], [2,0], [0,-1], T=1), 0)

        self.assertEqual(distance_similarity([0,0], [2,0], [0,0.5], T=10.0), 0.95)

    def test_line_distance__similarity(self):
        self.assertEqual(lineDistance_similarity([0, 0], [5, 2], [0, 0], [5, 2], T=1), 1)
        self.assertEqual(lineDistance_similarity([0, 0], [5, 2], [5, 2], [0, 0], T=1), 1)
        self.assertTrue(lineDistance_similarity([0, 0], [5, 2], [0, 0], [5, 1.9], T=1) > 0.95)
        self.assertTrue(lineDistance_similarity([0, 0], [5, 2], [0, 0], [5, 2.1], T=1) )
        self.assertTrue(lineDistance_similarity([0, 0], [1, 1], [1, 0], [0, 1], T=1) < 0.3)

    def test_line__similarity(self):
        self.assertTrue(isclose(line_similarity([0, 0], [5, 2], [0, 0], [5, 2]), 1))
        self.assertTrue(isclose(line_similarity([0, 0], [5, 2], [5, 2], [0, 0]), 1))
        self.assertTrue(isclose(line_similarity([0, 0], [5, 2], [0, 0], [5, 1.9]), 0.9534, err=0.01))
        self.assertTrue(isclose(line_similarity([0, 0], [5, 2], [0, 0], [5, 2.1]), 0.9498, err=0.01))
        self.assertTrue(isclose(line_similarity([0, 0], [1, 1], [1, 0], [0, 1]), 0))

    def test_segment__similarity(self):
        Aps = [[0.5, 0.5], [1, 1.5], [2, 2.5], [3.5, 3.5], [5.2, 4.5], [7.5, 6.5], [7.9, 8]]
        Bps = [[0.6, 0.5], [1.05, 1.45], [2.1, 2.4], [2.8, 4], [3.5, 5.5], [5, 5.7], [7.8, 5.7], [8.1, 6.5], [8.1, 8]]

        A = Segment(map(lambda p: Point(None, p[0], p[1], None), Aps))
        B = Segment(map(lambda p: Point(None, p[0], p[1], None), Bps))
        similarity, parts = segment_similarity(A, B)

        self.assertTrue(similarity > 0.35)
        self.assertTrue(parts[3] > parts[4])
        self.assertTrue(parts[4] < parts[5])
        # mid = sortSegmentPoints(Aps, Bps)

        # def plot(data, more=""):
            # plt.plot(map(lambda a: a[0], data), map(lambda a: a[1], data), more)
        # plot(Aps)
        # plot(Bps)

        # plot(mid)
        # kalm_res = kalman.kalman(mid)
        # plot(kalm_res, "ko-")

        # plt.show()



def isclose(a, b, err=1e-09):
    return abs(a-b) <= err

if __name__ == '__main__':
    unittest.main()

def testWithTracks():
    track1 = Track.fromGPX('/Users/ruipgil/tracks_bckp/2015-07-23_1.gpx')[0]
    track2 = Track.fromGPX('/Users/ruipgil/tracks_bckp/2015-07-23_3.gpx')[0]
    track1.preprocess()
    track2.preprocess()

    track1.toTrip()
    track2.toTrip()

    t1p = map(lambda p: p.gen2arr(), track1.segments[0].points)
    t2p = map(lambda p: p.gen2arr(), track2.segments[0].points)

    globalprox, part = segment_similarity(track1.segments[0], track2.segments[0])
    print(globalprox)

    # res = kalman(init)

    plt.axis('equal')
    def plot(data, more=""):
        plt.plot(map(lambda a: a[0], data), map(lambda a: a[1], data), more)
        # plt.plot(data[0][0], data[0][1], more+'o')
        # plt.plot(data[-1][0], data[-1][1], more+'o')
    plot(t1p)
    plot(t2p, 'k-')

    overlaps = []
    group = []
    for i, a in enumerate(part):
        if a > 0:
            group.append(t2p[i])
        elif len(group) > 0:
            overlaps.append(group)
            for j in group:
                plot(group)
            group = []
    plot(group)
    overlaps.append(group)

    print(len(overlaps))
    plt.show()

testWithTracks()
