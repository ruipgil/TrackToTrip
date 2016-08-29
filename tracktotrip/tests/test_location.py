"""
Location module unit tests
"""
import unittest
from tracktotrip import Point
from tracktotrip.location import update_location_centroid, compute_centroid

class TestLocation(unittest.TestCase):
    """
    Tests the location module
    """
    def assert_point(self, p_a, p_b):
        """ Checks if two points have the same position
        """
        self.assertEqual(p_a.lat, p_b.lat)
        self.assertEqual(p_a.lon, p_b.lon)

    def assert_points(self, points_a, points_b):
        """ Checks if two arrays of points have the same points, position-wise
        """
        self.assertEqual(len(points_a), len(points_b))
        for i, point_a in enumerate(points_a):
            point_b = points_b[i]
            self.assert_point(point_a, point_b)

    def test_compute_centroid(self):
        """ Tests compute_centroid function
        """
        centroid = compute_centroid([Point(0, 0, None).gen2arr()])
        self.assert_point(centroid, Point(0, 0, None))

        cluster = [Point(0, 0, None).gen2arr(), Point(5.0, 10.0, None).gen2arr()]
        centroid = compute_centroid(cluster)
        self.assert_point(centroid, Point(2.5, 5.0, None))

        cluster = [Point(5.0, 10.0, None).gen2arr(), Point(5.0, 10.0, None).gen2arr()]
        centroid = compute_centroid(cluster)
        self.assert_point(centroid, Point(5, 10, None))

    def test_ulc_empty_cluster(self):
        """ Tests update_location_centroid, with empty cluster
        """
        max_distance = 20
        min_samples = 2
        point = Point(30.0, -9.0, None)
        centroid, new_cluster = update_location_centroid(point, [], max_distance, min_samples)
        self.assert_point(centroid, point)
        self.assert_points(new_cluster, [point])

    def test_ulc_one_point_cluster(self):
        """ Tests update_location_centroid, using a cluster with one point
        """
        max_distance = 20
        min_samples = 2
        point = Point(30.0, -9.0, None)
        # points to far apart, should compute centroid from the two
        cluster = [Point(0.0, 0.0, None)]
        centroid, new_cluster = update_location_centroid(point, cluster, max_distance, min_samples)
        self.assert_point(centroid, Point(15.0, -4.5, None))
        self.assert_points(new_cluster, [Point(0.0, 0.0, None), point])

        # points close, both contribute
        cluster = [Point(30.0001, -8.9999, None)]
        centroid, new_cluster = update_location_centroid(point, cluster, max_distance, min_samples)
        self.assert_point(centroid, Point(30.00005, -8.99995, None))
        self.assert_points(new_cluster, [Point(30.0001, -8.9999, None), point])

    def test_ulc_points_cluster(self):
        """ Tests update_location_centroid, using a cluster with more than one point
        """
        max_distance = 20
        min_samples = 2
        point = Point(8.031852, 2.487095, None)
        p_1 = Point(8.03364868140281, 2.489711813527904, None)
        p_2 = Point(8.03364868140281, 2.489711813527904, None)
        cluster = [p_1, p_2]
        centroid, new_cluster = update_location_centroid(point, cluster, max_distance, min_samples)
        self.assert_point(centroid, Point(8.03364868140281, 2.489711813527904, None))
        self.assert_points(new_cluster, [p_1, p_2, point])

    def test_ulc(self):
        """ Tests update_location_centroid for centroid computation
        """
        max_distance = 20
        min_samples = 2
        p_1 = Point(8.0315188471279, 2.48728733258197, None)
        p_2 = Point(8.0335721637393, 2.4895146785343, None)
        p_3 = Point(8.0335721637393, 2.4895146785343, None)
        cluster = [p_1, p_2, p_3]
        point = Point(8.0318516937495, 2.48709511068233, None)
        centroid, new_cluster = update_location_centroid(point, cluster, max_distance, min_samples)
        self.assert_point(centroid, Point(8.0335721637393, 2.4895146785343, None))
        self.assert_points(new_cluster, [p_1, p_2, p_3, point])

if __name__ == '__main__':
    unittest.main()
