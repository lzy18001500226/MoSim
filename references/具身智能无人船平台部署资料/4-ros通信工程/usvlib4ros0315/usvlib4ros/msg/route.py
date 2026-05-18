
class Point:
    def __init__(self):
        self.lng = 0.0
        self.lat = 0.0
        self.high = 0.0
        self.cruiseSpeed = 0.0

        self.__msg = {}
        pass


class RouteMeta:

    def __init__(self):
        self.id = ''
        self.name = ''
        self.version = 0
        self.__msgDict = {'id':'','name':'',"version":0}

    def write(self):
        self.__msgDict['id'] = self.id
        self.__msgDict['name'] = self.name
        self.__msgDict['version'] = self.version
        return self.__msgDict

class Route:

    def __init__(self):
        self.id = ''
        self.name = ''
        self.version = 1
        self.startIndex = 0
        self.points = []
        self.obstacles = []

        self.__msg = {}
        pass

    def read(self,routeDict):
        """
        routeDict eg: {'id': '13', 'name': 'route-test2', 'version': 23,'points':[{'lng':138.451211,'lat':30.12451,'high':0,'cruiseSpeed':3.3}],'obstacles':[]}
        """
        self.id = routeDict['id']
        self.name = routeDict['name']
        self.version = routeDict['version']
        self.startIndex = routeDict['startIndex']

        points = routeDict['points']
        self.points = []
        for pointDict in points:
            point = Point()
            point.lng = pointDict['lng']
            point.lat = pointDict['lat']
            point.high = pointDict['high']
            point.cruiseSpeed = pointDict['cruiseSpeed']
            self.points.append(point)
            pass

        obstacles = routeDict['obstacles']
        self.obstacles = []
        for pointDict in obstacles:
            point = Point()
            point.lng = pointDict['lng']
            point.lat = pointDict['lat']
            point.high = pointDict['high']
            point.cruiseSpeed = pointDict['cruiseSpeed']
            self.obstacles.append(point)
            pass

        pass