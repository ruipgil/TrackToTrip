import gpxpy
import unittest
import tracktotrip as tt

def loadFile(name):
    return gpxpy.parse(open(name, 'r'))

class TestSegment(unittest.TestCase):
    def test_flow(self):
        track = tt.preprocess(loadFile("tracktotrip/tests/track.gpx"))
        segment = tt.segment(track)
        tt.utils.plotSegment(segment).show()
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
