#!/usr/bin/env python
#coding:utf-8

import math

from usvlib4ros.msg import Route,Point
from usvlib4ros.usvRosUtil import LogUtil,USVMathUtil


class RoutePlanService:

    Instance = None

    @classmethod
    def getInstancel(cls):
        if cls.Instance is None:
            cls.Instance = RoutePlanService()

        return cls.Instance

    def __init__(self,wayPointRadius = 5.0,route = Route()):

        self.routeId = -1
        self.versionWP = -1 #当前的路线版本号。
        self.wayPointRadius = wayPointRadius #导航点有效半径,m
        """update set"""
        self.curlongutude = 0.0
        self.curLatitude = 0.0
        self.route = route
        """temp"""
        self.changed2AutoReturning = 0 #是否刚刚切换到自动返航状态。0：非自动返航；1：刚刚切换到自动返航；2：已经处于自动返航状态。
        """get result"""
        self.distanceMetersShip2RouteLine = 0.0 #当前船到当前A->B导航线的距离（单位：米）
        self.shipDistanceA =0.0 #当前船到前一个导航点的距离。
        self.degreeAShip = 0.0 #以前一个导航点为圆心，到当前船的角度（正北为0）。
        self.degreeAB = 0.0 #以前一个导航点为圆心，到下一个导航点的角度（正北为0）。
        #self.degreeShipB = 0.0 #前一个船为圆心，到下一个导航点的角度（正北为0）
        self.distanceMetersShip2NextWP = 0.0 #当前船到下一个导航点的距离（单位：米）
        self.curPrevIndex = -1 #当前已通过导航点的索引号。
        self.curNextIndex = 0 #当前正前往的导航点的索引号。
        self.nextPoint = None
        self.prevPoint = None
        pass

    def reset(self,route):
        """
        采用接收的导航点集更新数据
        """
        self.changed2AutoReturning = 0
        self.curNextIndex = route.startIndex
        self.curPrevIndex = route.startIndex - 1
        self.route = route
        pass

    
    def setCurrentPos(self,longitude,latitude,isReturning = False):
        """calc self.curPrevIndex and self.curNextIndex in route.points[]"""
        route = self.route

        if isReturning :
            if self.changed2AutoReturning == 0:
                self.changed2AutoReturning = 1 #刚刚切换到自动返航状态。
            else:
                self.changed2AutoReturning = 2 #已经处于自动返航状态。
        else:
            self.changed2AutoReturning = 0 #处于非自动返航状态。

        self.curlongutude = longitude
        self.curLatitude = latitude

        try:
            self.calcNextWayPoint(isReturning=isReturning)
        except Exception as e:
            pass

        pointCount = len(route.points)
        prevPoint = None 
        nextPoint = None
        valid = True
        if self.curPrevIndex >= 0 and self.curPrevIndex < pointCount:
            prevPoint = route.points[self.curPrevIndex]
        if self.curNextIndex >= 0 and self.curNextIndex < pointCount:
            nextPoint = route.points[self.curNextIndex]

        if prevPoint is None or nextPoint is None:
            self.distanceMetersShip2RouteLine = 0

            if prevPoint is None:
                """如果是指向第一个导航点或者没有导航点。"""    
                self.shipDistanceA = 0
                if nextPoint is None:
                    """没有导航点时，AB点都设置为船当前位置"""
                    nextPoint = Point()
                    nextPoint.lng , nextPoint.lat = longitude,latitude
                    prevPoint = Point()
                    prevPoint.lng, prevPoint.lat = longitude, latitude
                    self.degreeAB = 0
                    """AB都不存在，输出无效"""
                    valid = False
                else:
                    """nextPoint指向第一个点，则将当前位置做为prevPoint"""
                    prevPoint = Point()
                    prevPoint.lng, prevPoint.lat = nextPoint.lng , nextPoint.lat
                    self.degreeAB = USVMathUtil.formatDegree(USVMathUtil.headingAB(longitude,latitude,nextPoint.lng,nextPoint.lat))
                self.degreeAShip = self.degreeAB
            else:
                """已没有其他目标，AB设置为同一点"""
                nextPoint = Point()
                nextPoint.lng, nextPoint.lat = prevPoint.lng, prevPoint.lat
                """如果是指向最后一个导航点或者没有导航点。"""
                self.shipDistanceA = USVMathUtil.calcGPSDistance(prevPoint.lng,prevPoint.lat,longitude,latitude)
                self.degreeAShip = USVMathUtil.formatDegree(USVMathUtil.headingAB(prevPoint.lng,prevPoint.lat,longitude,latitude))
                self.degreeAB = self.degreeAShip
        else:
            self.distanceMetersShip2RouteLine = self.getDistance2RouteLine(prevPoint.lng,prevPoint.lat,nextPoint.lng,nextPoint.lat,longitude,latitude)

        return valid,self.curNextIndex,nextPoint.lng,nextPoint.lat,prevPoint.lng,prevPoint.lat,self.distanceMetersShip2RouteLine,self.distanceMetersShip2NextWP,self.shipDistanceA

    
    def calcNextWayPoint(self,isReturning):
        route = self.route

        pointsCount = len(route.points) 
        if pointsCount == 0:
            self.distanceMetersShip2NextWP = 0
            self.distanceMetersShip2RouteLine = 0

            self.shipDistanceA = 0
            self.degreeAB = 0
            self.degreeAShip = 0

            self.curPrevIndex = -1
            self.curNextIndex = 0
            return 
            pass

        prevIndex = self.curPrevIndex
        nextIndex = self.curNextIndex

        if prevIndex >= pointsCount :
            """如果中途删除了节点，则使用最后一个节点作为当前目标导航点。"""
            nextIndex = pointsCount - 1
            prevIndex = nextIndex - 1
        if prevIndex < 0:
            prevIndex = -1
        """如果跑完了，总是围绕最后一个导航点转圈。"""
        if nextIndex >= pointsCount :
            nextIndex = pointsCount -1
            prevIndex = nextIndex -1

        """如果已经返回了，总是围绕第一个导航点转圈。"""
        if nextIndex < 0:
            nextIndex = 0
            prevIndex = -1

        self.curPrevIndex = prevIndex
        self.curNextIndex = nextIndex

        nextPoint = route.points[nextIndex]
        distance = USVMathUtil.calcGPSDistance(self.curlongutude,self.curLatitude,nextPoint.lng,nextPoint.lat)
        if distance > 20000 :
            """如果距离超过20km则认为导航点无效。"""
            self.distanceMetersShip2NextWP = distance
            return
        if isReturning and self.changed2AutoReturning == 1 :
            """如果是刚刚切换到自动返航状态，则遍历所有离当前第一个导航点最近的导航点，直接以切换到到该导航点的航线上。"""
            minDist = 10000000
            minIndex = 0
            index = 0
            for point in route.points:
                dist = USVMathUtil.calcGPSDistance(self.curlongutude,self.curLatitude,point.lng,point.lat)
                if dist < minDist:
                    minDist = dist
                    minIndex = index
                index = index +1

            prevIndex = minIndex
            if prevIndex <= 0:
                prevIndex = -1
                nextIndex = 0
            else:
                nextIndex = minIndex -1
            
            self.curPrevIndex = prevIndex
            self.curNextIndex = nextIndex

            nextPoint = route.points[nextIndex]
            distance = USVMathUtil.calcGPSDistance(self.curlongutude,self.curLatitude,nextPoint.lng,nextPoint.lat)
            self.distanceMetersShip2NextWP = distance
            return 
        
        """如果距离小于导航点有效半径，则认为已经到达该导航点。"""
        if distance < self.wayPointRadius:
            if isReturning :
                """如果是返航模式，则自动选择上一个导航点为NextPoint。"""
                if nextIndex <= 0:
                    """自动导航结束，总是围绕第一个点转圈。"""
                    nextIndex = 0
                    prevIndex = -1 
                else:
                    prevIndex = nextIndex
                    nextIndex = nextIndex -1
            else:
                """如果不是返航模式，则自动选择下一个导航点为NextPoint。"""
                if nextIndex >= pointsCount -1 :
                    """自动导航结束，总是围绕最后一个点转圈。"""
                    nextIndex = pointsCount -1
                    prevIndex = nextIndex -1
                else:
                    prevIndex = nextIndex
                    nextIndex = nextIndex +1
            self.curPrevIndex = prevIndex
            self.curNextIndex = nextIndex

            nextPoint = route.points[nextIndex]
            distance = USVMathUtil.calcGPSDistance(self.curlongutude,self.curLatitude,nextPoint.lng,nextPoint.lat)

        self.distanceMetersShip2NextWP = distance                
        pass


    def getDistance2RouteLine(self,longitudeA,latitudeA,longitudeB,latitudeB,longitudeShip,latitudeShip):
        shipDistanceA = USVMathUtil.calcGPSDistance(longitudeA,latitudeA,longitudeShip,latitudeShip)
        degreeAShip = USVMathUtil.formatDegree(USVMathUtil.headingAB(longitudeA,latitudeA,longitudeShip,latitudeShip))
        degreeAB = USVMathUtil.formatDegree(USVMathUtil.headingAB(longitudeA,latitudeA,longitudeB,latitudeB))
        degreeShipAB = (degreeAShip - degreeAB ) * math.pi / 180
        distance = shipDistanceA * math.sin(degreeShipAB)

        self.shipDistanceA = shipDistanceA
        self.degreeAB = degreeAB
        self.degreeAShip = degreeAShip
        return distance
        pass
    pass