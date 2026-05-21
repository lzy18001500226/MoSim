from pathlib import Path
from rosbags.highlevel import AnyReader

"""
pip install rosbags -i https://pypi.tuna.tsinghua.edu.cn/simple

https://ternaris.gitlab.io/rosbags/topics/rosbag1.html
"""


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


if __name__ == "__main__":
    path = 'rosbag/1.bag'
    topic = '/usv/001/scada/ctl/action/pose'

    rosbagUtil = RosBagUtil(path)
    topicArray = rosbagUtil.getRosBagTopicList()

    field = rosbagUtil.getTopicMsgField(topic)
    msgArray = rosbagUtil.getTopicMsgList(topic)
    print(msgArray)