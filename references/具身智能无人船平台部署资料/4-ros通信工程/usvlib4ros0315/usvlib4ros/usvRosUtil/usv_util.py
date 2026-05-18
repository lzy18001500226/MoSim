#!/usr/bin/env python
#coding:utf-8

import struct
import math


class USVMathUtil:
    
    EARTH_RADIUS = 6378.137 #km

    @classmethod
    def quaternionToEulerAngles(cls,w,x,y,z):
        """四元数（w,x,y,z）转欧拉角（单位：°）,旋转顺序 Z-Yaw、Y-Pitch、X-Roll"""
        # 转换为欧拉角
        t0 = 2.0 * (w * x + y * z)
        t1 = 1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(t0, t1)

        t2 = 2.0 * (w * y - z * x)
        pitch = math.asin(t2)

        t3 = 2.0 * (w * z + x * y)
        t4 = 1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(t3, t4)

        # 将弧度转换为角度
        roll_deg = math.degrees(roll)
        pitch_deg = math.degrees(pitch)
        yaw_deg = math.degrees(yaw)
        return roll_deg,pitch_deg,yaw_deg

    @classmethod
    def eulerAngleToQuaternion(cls,roll,pitch,yaw):
        """欧拉角（单位：°）转四元数：w，x，y，z；旋转顺序 Z-Yaw、Y-Pitch、X-Roll"""
        r = math.radians(roll)
        p = math.radians(pitch)
        y = math.radians(yaw)
        w = math.cos(y / 2) * math.cos(p / 2) * math.cos(r / 2) + math.sin(y / 2) * math.sin(p / 2) * math.sin(r / 2)
        x = math.sin(y / 2) * math.cos(p / 2) * math.cos(r / 2) - math.cos(y / 2) * math.sin(p / 2) * math.sin(r / 2)
        y = math.cos(y / 2) * math.sin(p / 2) * math.cos(r / 2) + math.sin(y / 2) * math.cos(p / 2) * math.sin(r / 2)
        z = math.cos(y / 2) * math.cos(p / 2) * math.sin(r / 2) - math.sin(y / 2) * math.sin(p / 2) * math.cos(r / 2)
        return w,x,y,z

    @classmethod
    def formatDegree(cls,degree):
        if degree >= 360 or degree <= -360 :
            times = int(degree / 360)
            degree = degree - times * 360

        if degree < 0:
            degree = degree + 360
        return degree
        pass

    @classmethod
    def angleToRadian(cls,degree):
        """ ° =》 rad """
        return degree * math.pi / 180
        pass

    @classmethod
    def calcGPSDistance(cls,lng1,lat1,lng2,lat2):
        """
        lng1,lat1 : point1 gps \r\n
        lng2,lat2 : point2 gps
        采用直线距离近似计算球面弧线距离，适用20km以内的两点
        结果保留小数点后一位，单位m
        """
        radLat1 = cls.angleToRadian(lat1)
        radLat2 = cls.angleToRadian(lat2)
        a = radLat1 - radLat2
        b = cls.angleToRadian(lng1) - cls.angleToRadian(lng2)
        s = 2 * math.asin(math.sqrt(math.pow(math.sin(a/2),2) + math.cos(radLat1)* math.cos(radLat2)*math.pow(math.sin(b/2),2)))
        s = s * cls.EARTH_RADIUS * 1000     # m
        s = round(s,1)      #结果保留小数点后一位，单位m
        return s
        pass

    @classmethod
    def headingAB(cls,lngA,latA,lngB,latB):
        """
        计算以A点为原点，到B点的heading度数。\r\n
        正北为0°，东正西负。\r\n
        """
        deltaLng = lngB - lngA
        deltaLat = latB - latA
        angle = math.atan2(deltaLat,deltaLng)  
        headingRad = math.pi / 2 - angle

        pi2 = math.pi * 2
        if angle > pi2 or angle < -pi2:
            times = int(angle / pi2)
            headingRad = headingRad - times * pi2
        if headingRad < 0:
            headingRad = headingRad + pi2

        headingDegree = headingRad * 180 / math.pi
        return headingDegree
        pass

class USVByteUtil:

    @classmethod
    def floatPack(cls,value):
        """
        Python  | C/C++ \r\n
        ------------------- \r\n
        float   | double \r\n
        int     | int64 \r\n
        value = 1.0 , return '4607182418800017408'
        """
        doubleBytes =  struct.pack("<d",value)
        uint64Value = struct.unpack('<Q',doubleBytes)[0]
        uint64Str = str(uint64Value)
        return uint64Str
        pass

    @classmethod
    def floatUnpack(cls,uint64Str):
        """
        Python  |   C/C++ \r\n
        ------------------- \r\n
        float   |   double  \r\n
        int     |   int64   \r\n
        uint64Str = "4607182418800017408" return 1.0
        """
        uint64Value = int(uint64Str,10)
        uint64Bytes = struct.pack('<Q',uint64Value)
        value = struct.unpack("<d",uint64Bytes)[0]
        return value

