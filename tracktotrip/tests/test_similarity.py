"""
Unit tests for similarity module
"""
import math
import unittest
from tracktotrip.similarity import segment_similarity
from tracktotrip.similarity import normalize, line_distance_similarity, line_similarity
from tracktotrip.similarity import line, angle_similarity, distance_to_line, distance_similarity
from tracktotrip import Segment, Point

class TestSimilarity(unittest.TestCase):
    """
    Tests similarity
    """
    def test_angle_similarity(self):
        """ Tests angle_similarity function
        """
        l1p1 = [10, 10]
        l1p2 = [10, 12]
        l_1 = line(l1p1, l1p2)

        l2p1 = [11, 10]
        l2p2 = [10, 10]
        l_2 = line(l2p1, l2p2)

        self.assertEqual(angle_similarity(normalize(l_1), normalize(l_2)), 0)
        self.assertEqual(
            angle_similarity(normalize([0, 1]), normalize([1, 1])),
            angle_similarity(normalize([1, 0]), normalize([1, 1])))
        self.assertEqual(angle_similarity(normalize([0, 1]), normalize([0, -1])), -1)

    def test_distance(self):
        """ Test distance_to_line function
        """
        sqrt2 = math.sqrt(2)
        self.assertEqual(distance_to_line([0, 0], [4, 2], [0, 0]), 0)
        self.assertEqual(distance_to_line([0, 0], [4, 2], [4, 2]), 0)
        self.assertEqual(distance_to_line([0, 0], [4, 2], [2, 1]), 0)
        self.assertEqual(distance_to_line([0, 0], [2, 2], [0, 2]), sqrt2)
        self.assertEqual(distance_to_line([0, 0], [2, 2], [3, 3]), sqrt2)

    def test_distance_similarity(self):
        """ Tests distance_similarity function
        """
        self.assertEqual(distance_similarity([0, 0], [4, 2], [0, 0], T=1), 1)
        self.assertEqual(distance_similarity([0, 0], [4, 2], [4, 2], T=1), 1)
        self.assertEqual(distance_similarity([0, 0], [4, 2], [2, 1], T=1), 1)

        self.assertEqual(distance_similarity([0, 0], [2, 0], [0, 1], T=1), 0)
        self.assertEqual(distance_similarity([0, 0], [2, 0], [0, 0.5], T=1), 0.5)
        self.assertEqual(distance_similarity([0, 0], [2, 0], [0, -1], T=1), 0)

        self.assertEqual(distance_similarity([0, 0], [2, 0], [0, 0.5], T=10.0), 0.95)

    def test_line_distance_similarity(self):
        """ Tests line_distance_similarity function
        """
        self.assertEqual(line_distance_similarity([0, 0], [5, 2], [0, 0], [5, 2], T=1), 1)
        self.assertEqual(line_distance_similarity([0, 0], [5, 2], [5, 2], [0, 0], T=1), 1)
        self.assertTrue(line_distance_similarity([0, 0], [5, 2], [0, 0], [5, 1.9], T=1) > 0.95)
        self.assertTrue(line_distance_similarity([0, 0], [5, 2], [0, 0], [5, 2.1], T=1))
        self.assertTrue(line_distance_similarity([0, 0], [1, 1], [1, 0], [0, 1], T=1) < 0.3)

    def test_line_similarity(self):
        """ Tests line_similarity function
        """
        self.assertTrue(isclose(line_similarity([0, 0], [5, 2], [0, 0], [5, 2]), 1))
        self.assertTrue(isclose(line_similarity([0, 0], [5, 2], [5, 2], [0, 0]), 1))
        self.assertTrue(isclose(
            line_similarity([0, 0], [5, 2], [0, 0], [5, 1.9]), 0.9534, err=0.01))
        self.assertTrue(isclose(
            line_similarity([0, 0], [5, 2], [0, 0], [5, 2.1]), 0.9498, err=0.01))
        self.assertTrue(isclose(line_similarity([0, 0], [1, 1], [1, 0], [0, 1]), 0))

    def test_segment_similarity(self):
        """ Tests segment_similarity function
        """
        a_pts = [
            [0.5, 0.5],
            [1, 1.5],
            [2, 2.5],
            [3.5, 3.5],
            [5.2, 4.5],
            [7.5, 6.5],
            [7.9, 8]
        ]
        b_pts = [
            [0.6, 0.5],
            [1.05, 1.45],
            [2.1, 2.4],
            [2.8, 4],
            [3.5, 5.5],
            [5, 5.7],
            [7.8, 5.7],
            [8.1, 6.5],
            [8.1, 8]
        ]

        a_seg = Segment([Point(p[0], p[1], None) for p in a_pts])
        b_seg = Segment([Point(p[0], p[1], None) for p in b_pts])
        similarity, parts = segment_similarity(a_seg, b_seg)

        self.assertTrue(similarity > 0.35)
        self.assertTrue(parts[3] > parts[4])
        self.assertTrue(parts[4] < parts[5])

def isclose(one, two, err=1e-09):
    """ Check if two number are close enought

    Args:
        one (float)
        two (float)
    Returns:
        bool
    """
    return abs(one-two) <= err

if __name__ == '__main__':
    unittest.main()
