from tracktotrip import learn_trip, Track, Segment, Point
from datetime import datetime, timedelta
import unittest

class TestLearnTrip(unittest.TestCase):
    def setUp(self):
        Aps = [[0.5, 0.5], [1, 1.5], [2, 2.5], [3.5, 3.5], [5.2, 4.5], [7.5, 6.5], [7.9, 8]]
        Bps = [[0.6, 0.5], [1.05, 1.45], [2.1, 2.4], [2.8, 4], [3.5, 5.5], [5, 5.7], [7.8, 5.7], [8.1, 6.5], [8.1, 8]]

        time = datetime.now()
        dt = timedelta(1000)

        def pt_arr_to_track(pts):
            seg = Segment(map(lambda p: Point(None, p[0], p[1], time + dt), pts))
            return Track(name="TripA", segments=[seg])

        self.tripA = pt_arr_to_track(Aps)
        self.tripA.toTrip(name="A")

        self.tripB = pt_arr_to_track(Bps)
        self.tripB.toTrip(name="B")

    def fail(self, track):
        self.assertTrue(False)


    def test_empty_list(self):
        # print(len(self.tripA.segments[0].points))
        def expected(track):
            # print(len(track.segments[0].points))
            self.assertTrue(True)

        learn_trip.learn_trip(self.tripA, [], expected, self.fail)

    def test_exact_matching_track(self):
        def expected(track):
            self.assertTrue(True)

        learn_trip.learn_trip(self.tripA, [self.tripA.copy()], self.fail, expected)

    def test_matching_track(self):
        def expected(track):
            self.assertTrue(True)

        learn_trip.learn_trip(self.tripA, [self.tripB], self.fail, expected)


if __name__ == '__main__':
    unittest.main()
