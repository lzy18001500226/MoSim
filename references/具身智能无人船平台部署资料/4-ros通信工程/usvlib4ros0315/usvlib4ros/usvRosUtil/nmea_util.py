import re


class NMEAUtil:

    @classmethod
    def calculate_nmea_checksum(cls,nmea_sentence:str):
        """calculate nmea check sum"""
        nmea_sentence = nmea_sentence.strip('$').rstrip('*')
        if '*' in nmea_sentence:
            nmea_sentence = nmea_sentence.split('*')[0]

        checksum = 0
        for char in nmea_sentence:
            checksum ^= ord(char)

        checksum_hex = format(checksum,'02X')
        return checksum_hex
        pass

    @classmethod
    def validate_nmea_checksum(cls,nmea_sentence):
        parts = nmea_sentence.split('*')
        if len(parts) < 2 :
            # 没有找到校验和
            return False

        checksum = cls.calculate_nmea_checksum(nmea_sentence)
        result = checksum.upper() == parts[-1].upper()
        return result
        pass

    @classmethod
    def parse_gpgga(cls,nmea_sentence):
        """
        # GPGGA语句的格式通常是：$GPGGA,<1>,<2>,<3>,<4>,<5>,<6>,<7>,<8>,<9>,<10>,<11>,<12>*hh<CR><LF>
        # <1> UTC时间
        # <2> 纬度ddmm.mmmmm
        # <3> 纬度半球N（北半球）或S（南半球）
        # <4> 经度dddmm.mmmmm
        # <5> 经度半球E（东经）或W（西经）
        # <6> 定位质量（0=无效定位，1=GPS定位，...）
        # <7> 使用卫星数量
        # <8> 水平精确度
        # <9> 海拔高度（单位：米）
        # <10> M（海拔高度单位：米）
        # <11> 地球椭球面相对大地水准面的高度（单位：米）
        # <12> M (地球椭球面相对大地水准面的高度单位：米）
        # <13> 差分GPS数据期限（RTCM SC-104）
        # <14> 差分参考基站标号（0000-1023）
        :return: fix_quality<6>,num_sats<7>,hdop<8>,altitude<9>,geoid_sep<10>
        """
        fix_quality = 0
        num_sats = 0
        hdop = 0.0
        altitude = 0.0
        geoid_sep = 0.0

        fields = re.split(r'[,*]', nmea_sentence)
        if fields[0] != '$GPGGA':
            return fix_quality,num_sats,hdop,altitude,geoid_sep
        if len(fields) != 16:
            return fix_quality, num_sats, hdop, altitude, geoid_sep
        if fields[6] == '' or fields[6] == '0':
            return fix_quality, num_sats, hdop, altitude, geoid_sep

        fix_quality = int(fields[6]) #0=无效定位，1=GPS定位，2DGPS , 3 RTK...
        num_sats = int(fields[7])    #使用卫星数量
        hdop = float(fields[8])        # 水平精确度（HDOP）
        altitude = float(fields[9])    # 海拔高度（单位：米）
        geoid_sep = float(fields[11])  # 地球椭球面相对大地水准面的高度（单位：米）
        return fix_quality, num_sats, hdop, altitude, geoid_sep
        pass

    @classmethod
    def parse_gpgsa(cls, nmea_sentence):
        """GPGSA语句包含了当前定位所使用的卫星的PRN（伪随机噪声）编号、定位类型（如2D、3D）以及不同的精度衰减因子（DOP，如PDOP、HDOP、VDOP）"""
        """nothing used"""
        pass

    @classmethod
    def parse_gphdt(cls, nmea_sentence):
        """
        语句提供了真北方向（相对于地理北极）的磁罗盘航向信息
        # GPHDT语句的格式通常是：$GPHDT,<1>*hh<CR><LF>
        # <1> 磁罗盘航向，000.0 到 359.9 度
        """
        # 使用逗号分割字符串
        fields = re.split(r'[,*]', nmea_sentence)
        valid = False
        true_heading = 0.0

        # 检查字段数量是否至少为2（包括航向）
        if len(fields) != 3:
            return valid ,true_heading

        # 提取航向字段
        true_heading = float(fields[1])
        return valid ,true_heading
        pass

    @classmethod
    def parse_gprmc(cls, nmea_sentence):
        """
        # GPRMC语句的格式通常是：$GPRMC,<1>,<2>,<3>,<4>,<5>,<6>,<7>,<8>,<9>,<10>,<11>*hh<CR><LF>
        # <1>是UTC时间，
        # <2>是状态（A=有效定位，V=无效定位），
        # <3>是纬度，
        # <4>是纬度半球N或S，
        # <5>是经度，
        # <6>是经度半球E或W，
        # <7>是地面速度（节），
        # <8>是地面航向（度真北），
        # <9>是UTC日期，
        # <10>是磁偏角（度），
        # <11>是磁偏角方向（E或W）
        :return: valid,utc_time,date,lng,lat,speed,heading
        """
        valid = False
        utc_time  = ''
        lng = 0.0
        lat = 0.0
        speed = 0.0
        heading = 0.0
        date = ''

        fields = re.split(r'[,*]', nmea_sentence)
        if fields[0] != '$GPRMC':
            return valid,utc_time,date,lng,lat,speed,heading
        if len(fields) != 13:
            return valid,utc_time,date,lng,lat,speed,heading

        if fields[2] == "A" : #A=有效定位，V=无效定位。
            valid = True
            utc_time = fields[1] #UTC时间，格式如：hhmmss.sss
            date = fields[9]     #UTC日期，ddmmyy格式
            lat = fields[3]      # 纬度，ddmm.mmmmm格式
            lat_hemi = fields[4] # 纬度半球，N或S
            lng = fields[5]      # 经度，dddmm.mmmmm格式
            lng_hemi = fields[6] # 经度半球，E或W
            speed = float(fields[7]) # 地面速度，节
            heading = float(fields[8])   # 地面航向，度真北

            # 转换纬度和经度为度格式（dd.ddddd）
            lat_deg = float(lat[:2]) + float(lat[2:]) / 60.0
            if lat_hemi == 'S':
                lat_deg = -lat_deg

            lng_deg = float(lng[:3]) + float(lng[3:]) / 60.0
            if lng_hemi == 'W':
                lng_deg = -lng_deg
        else:
            """无效定位"""
            valid = False

        return valid, utc_time,date, lng_deg, lat_deg, speed, heading
        pass

    @classmethod
    def socketBuffSplit(cls,buff):
        return buff.split("\r\n")
        pass


if __name__ == "__main__":
    buff = '$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A\r\n$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n'
    nmea_sentence_list = NMEAUtil.socketBuffSplit(buff)
    for nmea_sentence in nmea_sentence_list:
        result = NMEAUtil.validate_nmea_checksum(nmea_sentence)

        if result is False:
            continue

        if nmea_sentence.startswith('$GPRMC'):
            NMEAUtil.parse_gprmc(nmea_sentence)
        elif nmea_sentence.startswith('$GPGGA'):
            NMEAUtil.parse_gpgga(nmea_sentence)


    pass