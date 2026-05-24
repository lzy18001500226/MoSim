#!/usr/bin/env python
#coding:utf-8

import math

from usvlib4ros.usvRosUtil import LogUtil,USVMathUtil


class AutoPilotService:

    def __init__(self):
        """set"""
        self.cruiseSpeed = 5.0  #unity设置的导航点巡航速度 m/s
        self.maxSpeed = 5.0     #船物理速度限制 m/s
        self.maxRotateSpeed = 40   #船最大物理转向速度 °/s
        self.routeWPRadius = 2.5 #导航点有效半径 m
        #航道宽度 m
        
        """get result"""
        self.advisedSpeed = 0.0         # m/s
        self.advisedRotateSpeed = 0.0   # °/s
        self.advisedHeading = 0.0       #前一个船为圆心，到下一个导航点的角度（正北为0）
        pass

    def setConditions(self,curSpeed,curHeading,curLng,curLat,destLng,destLat,prevLng,prevLat,shipToPrevWPDistance,shipToNextWPDistance,shipToRouteDistance):
        # if shipToNextWPDistance < self.routeWPRadius :
        #     """"""
        #     self.advisedSpeed = 0.0         # m/s
        #     self.advisedRotateSpeed = 0.0   # °/s
        #     self.advisedHeading = 0.0 #
        #     return 
        
        """先进行坐标系转换，以prev导航点A为原点，dest导航点B为North（0度）方向。"""
        headingPrev2Ship = USVMathUtil.formatDegree(USVMathUtil.headingAB(prevLng,prevLat,curLng,curLat))
        headingPrev2Next = USVMathUtil.formatDegree(USVMathUtil.headingAB(prevLng,prevLat,destLng,destLat))

        distanceAB =  USVMathUtil.calcGPSDistance(prevLng,prevLat,destLng,destLat)
        degreeShipB = USVMathUtil.formatDegree(USVMathUtil.headingAB(curLng,curLat,destLng,destLat))

        degreeShipAB = headingPrev2Ship - headingPrev2Next
        radShipAB = USVMathUtil.angleToRadian(degreeShipAB)

        distanceRouteX = shipToRouteDistance
        distanceRouteY = shipToPrevWPDistance * math.cos(radShipAB)

        distanceRouteYB = distanceAB - distanceRouteY

        direct2WP = 0 #是否直行到A或B导航点。
        if abs(distanceRouteYB) >= abs(distanceAB):
            """如果当前船在A->B连线（A在原点，B总是在正北方）的下方，则直接行驶到导航点A。"""
            direct2WP = 1 #直接行使到A

        if distanceRouteYB <= 0:
            """如果当前船在A->B连线（A在原点，B总是在正北方）的上方，则直接行驶到导航点B。"""
            direct2WP = 2 #直接行使到B
        if abs(distanceRouteYB) < self.routeWPRadius or abs(distanceRouteX) < self.routeWPRadius :
            """如果距离B导航点纵坐标或横坐标之一在5米之内，则直行到导航点A或B。"""
            direct2WP = 2 #直接行使到B

        advisedHeading = 0.0
        distance4Calc = 0.0

        if direct2WP == 1 :
            """直接行使到A。"""
            advisedHeading = USVMathUtil.formatDegree(headingPrev2Ship + 180)
            distance4Calc = shipToPrevWPDistance
        elif direct2WP == 2 :
            """直接行使到B。"""
            advisedHeading = degreeShipB
            distance4Calc = shipToNextWPDistance
        else:
            """"""
            simbolFlag = 1 
            if distanceRouteX >= 0 : 
                simbolFlag = -1 
            degreeCut = self.calcDegreeCutByDistance(abs(distanceRouteX))
            advisedHeading =  USVMathUtil.formatDegree(headingPrev2Next + degreeCut * simbolFlag)

            if degreeCut > 45 :
                distance4Calc = distanceRouteX
            else:
                distance4Calc = 1000

        #TODO
        if advisedHeading > 180:
            advisedHeading = advisedHeading - 360
        elif advisedHeading < -180:
            advisedHeading = advisedHeading + 360
            
        # LogUtil.info("heading (%s => %s)"%(curHeading,advisedHeading))
        self.advisedHeading = advisedHeading 
        degree4Calc = advisedHeading - curHeading 
        if degree4Calc > 180 :
            degree4Calc = degree4Calc -360
        elif degree4Calc < -180:
            degree4Calc = degree4Calc + 360

        self.advisedSpeed ,self.advisedRotateSpeed  = self.toPrecent(distance4Calc,degree4Calc)
        return self.advisedSpeed ,self.advisedRotateSpeed,self.advisedHeading

    def toPrecent(self,shipToNextWPDistance,shipHeadingToB):
        MAX_SPEED = self.maxSpeed #m/s
        MAX_ROTATE = self.maxRotateSpeed #°/s 
        speedPrecent = 1 #[-100,100]
        rotatePrecent = 1 #[-100,100]

        if shipToNextWPDistance < 0 :
            speedPrecent = -1
        if shipHeadingToB < 0:
            rotatePrecent = -1

        if abs(shipToNextWPDistance) > MAX_SPEED:
            shipToNextWPDistance = MAX_SPEED * speedPrecent
        if abs(shipHeadingToB) > MAX_ROTATE:
            shipToNextWPDistance = shipToNextWPDistance / 4
            shipHeadingToB = MAX_ROTATE * rotatePrecent
        
        rotatePrecent = int(shipHeadingToB * 100 / MAX_ROTATE) #[-100,100]
        speedPrecent = int(shipToNextWPDistance * 100 / MAX_SPEED ) #[-100,100]
        
        # if abs(rotatePrecent) > 30:
        #     speedPrecent = 0

        return speedPrecent, rotatePrecent


    def calcDegreeCutByDistance(self,absDistance2Route):
        """"""
        x = absDistance2Route
        x2 = absDistance2Route * absDistance2Route
        cutDegree = -0.008316 * x2 + 2.023147 * x
        if cutDegree < 0 :
            cutDegree = 0
        elif cutDegree > 90 :
            cutDegree = 90
        return cutDegree
    
    def calcLimitedSpeedByDistance(self,absDistance):
        """到达目的地时的降速处理。"""
        advisedMaxSpeedKM = 1000 #不限速。
        if absDistance < 15 :
            """如果距离导航点还有15米，将速度降到10km/h左右。"""
            advisedMaxSpeedKM = 10

        return advisedMaxSpeedKM

    pass