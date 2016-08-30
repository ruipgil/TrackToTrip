from tracktotrip import Track
import numpy as np
import matplotlib.pyplot as plt

temp_trk = [
    Track.from_gpx('/Users/ruipgil/tracks/backup/2015-07-23_1.gpx')[0],
    Track.from_gpx('/Users/ruipgil/tracks/backup/2015-07-23_2.gpx')[0],
    Track.from_gpx('/Users/ruipgil/tracks/backup/2015-07-23_3.gpx')[0]
]

segs = []
for trke in temp_trk:
    segs.extend(trke.segments)
trk = Track("", segs)
trk.compute_metrics()
# trk.to_trip('', 0, 5.0, 0.15, 80, 0.3, '%Y-%m-%d')
plt.axis('equal')
for segment in trk.segments:
    plt.plot([p.lon for p in segment.points], [p.lat for p in segment.points], '-')

n_points = sum([len(s.points) for s in trk.segments])
trk.simplify(None, None)
for segment in trk.segments:
    plt.plot([p.lon for p in segment.points], [p.lat for p in segment.points], '--')
result = sum([len(s.points) for s in trk.segments])
print("From %d to %d points" % (n_points, result))
print("Compression: %f" % (n_points/float(result)))

plt.show()
