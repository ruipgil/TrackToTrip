LOCATION_KB = []
def matchLocation(position):
    distances = []
    for loc in LOCATION_KB:
        distances.append({
            'distance': loc.distance(position),
            'location': loc
            })
    print(LOCATION_KB, distances)
    distances = filter(lambda d: d['distance'] >= LOC_THRESHOLD, distances)

    print(distances)
    if len(distances) > 0:
        distances = sorted(distances, key=lambda d: d['distance'])
        return distances[-1]['location']
    else:
        newLoc = Location("#" + str(len(LOCATION_KB)), position)
        LOCATION_KB.append(newLoc)
        return newLoc

def inferLocation(segment):
    start = segment[0]
    end = segment[-1]
    return matchLocation(start), matchLocation(end)


# 5 meters is the threshold
LOC_THRESHOLD = 100

class Location:
    def __init__(self, label, position):
        self.label = label
        self.centroid = position
    def match(self, position):
        distance = self.centroid.distance(position)
        print(distance)
        return distance <= LOC_THRESHOLD
    def distance(self, position):
        return self.centroid.distance(position)

    def toJSON(self):
        return {
                'label': self.label,
                'position': self.centroid.toJSON()
                }
    @staticmethod
    def fromJSON(json):
        return Location(json['label'], json['position'])
