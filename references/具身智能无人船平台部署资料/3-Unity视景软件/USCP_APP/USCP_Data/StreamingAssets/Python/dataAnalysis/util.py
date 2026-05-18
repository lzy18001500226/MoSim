from rosbagUtil import RosBagUtil
import random
import colorsys
import sys
import json

class Util:
    @staticmethod
    def get_all_info(path):
        rosbagUtil = RosBagUtil(path)
        topics = rosbagUtil.getRosBagTopicList()
        pair_dict = {}
        for topic in topics:
            fields = rosbagUtil.getTopicMsgField(topic)
            pair_dict.update({topic: fields})
        print(pair_dict)
        json_string = json.dumps(pair_dict, indent=4)
        return pair_dict
    
    @staticmethod
    def random_color():
        hue = random.random()
        saturation = 0.5 + random.random() * 0.5 
        value = 0.4 + random.random() * 0.6 
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return (r, g, b)

if __name__ == '__main__':
    Param1 = sys.argv[1]
    Util.get_all_info(Param1)
    