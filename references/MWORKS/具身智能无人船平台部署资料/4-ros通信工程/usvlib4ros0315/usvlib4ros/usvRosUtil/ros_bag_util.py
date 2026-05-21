
"""
pip install rosbags -i https://pypi.tuna.tsinghua.edu.cn/simple

https://ternaris.gitlab.io/rosbags/topics/rosbag1.html
"""

from pathlib import Path
from rosbags.highlevel import AnyReader

import sys


class RosBagUtil:

    def __init__(self,path):
        self.path = Path(path)

    def getRosBagTopicList(self):
        topicArray = []
        with AnyReader([self.path]) as reader:
            for conn in reader.connections:
                topicArray.append(conn.topic)
        return topicArray

    def getTopicMsgList(self,topic):
        msgArray = []
        with AnyReader([self.path]) as reader:
            connections = [x for x in reader.connections if x.topic == topic]
            for connection, timestamp, rawdata in reader.messages(connections=connections):
                msg = reader.deserialize(rawdata,typ=connection.msgtype)
                msgArray.append(msg)
        return msgArray
        pass

    def getTopicMsgFieldList(self,topic,field):
        datas = []
        with AnyReader([self.path]) as reader:
            connections = [x for x in reader.connections if x.topic == topic]
            for connection, timestamp, rawdata in reader.messages(connections=connections):
                msg = reader.deserialize(rawdata,typ=connection.msgtype)
                data = msg.__getattribute__(field)
                datas.append((timestamp,data))
        return datas
        pass

    def getTopicMsgField(self,topic):
        fieldArray = []
        with AnyReader([self.path]) as reader:
            for connection in reader.connections :
                if connection.topic == topic:
                    """connection.msgdef 示例如下：返回字符串中 ‘================================================================================’ 之前的是有效字段，之后的是系统填充信息（无效字段）"""
                    """
                    std_msgs/Header header
                    float64 lng
                    float64 lat
                    float64 high
                    float64 roll
                    float64 pitch
                    float64 yaw
                    float64 speed
                    float64 rotateSpeed
                    ================================================================================
                    MSG: std_msgs/Header
                    # Standard metadata for higher-level stamped data types.
                    # This is generally used to communicate timestamped data 
                    # in a particular coordinate frame.
                    # 
                    # sequence ID: consecutively increasing ID 
                    uint32 seq
                    #Two-integer timestamp that is expressed as:
                    # * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
                    # * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
                    # time-handling sugar is provided by the client library
                    time stamp
                    #Frame this data is associated with
                    string frame_id
                    """
                    msgDefStr = connection.msgdef
                    msgLines = msgDefStr.splitlines()
                    for line in msgLines:
                        line = line.strip()
                        if line == "":
                            continue
                        if line.startswith('====='):
                            break

                        fields = line.split(' ')
                        fieldArray.append({fields[1]:fields[0]})
        return fieldArray
        pass

#python xxx.py path topic1 filed1 topic2 filed2 ...topicn filedn
if __name__ == "__main__":
    argv_len = len(sys.argv)
    print(sys.argv)

    path = sys.argv[1]
    
    topic = '/usv/001/ctl/scada/action'

    """获取bag文件中的所有话题"""
    # rosbagUtil = RosBagUtil(path)
    # topicArray = rosbagUtil.getRosBagTopicList()
    # print(topicArray)
    #
    # """获取bag文件中指定话题包含那些字段"""
    # field = rosbagUtil.getTopicMsgField(topic)
    # print(field)
    #
    # """获取bag文件中指定话题包含的所有数据"""
    # msgArray = rosbagUtil.getTopicMsgList(topic)
    # print(msgArray)
    #
    # """获取bag文件中指定话题中指定字段的所有数据"""
    # datas = rosbagUtil.getTopicMsgFieldList(topic,'lng')
    # print(datas)
    pass