class Point:
    def __init__(self, index, lat, lon, time, dt=0, acc=0.0, vel=0.0):
        self.data = [index, lon, lat, time, dt, acc, vel]
    def getId(self):
        return self.data[0]
    def getLat(self):
        return self.data[2]
    def setLat(self, lat):
        self.data[2] = lat
    def getLon(self):
        return self.data[1]
    def setLon(self, lon):
        self.data[1] = lon
    def getTime(self):
        return self.data[3]
    def getDt(self):
        return self.data[4]
    def getAcc(self):
        return self.data[5]
    def getVel(self):
        return self.data[6]
    def gen2arr(self):
        return [self.data[1], self.data[2]]
    def gen3arr(self):
        return [self.data[1], self.data[2], self.getTime()]
    def __repr__(self):
        return self.data.__repr__()
