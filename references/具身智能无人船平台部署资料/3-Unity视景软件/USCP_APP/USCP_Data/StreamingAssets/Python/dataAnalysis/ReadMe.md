[脚本格式]
python main.py [path] [topic] [field] [topic] [field] ......

[示例]
python main.py rosbag/1.bag /usv/001/scada/ctl/action/pose rotateSpeed /usv/001/scada/ctl/action/pose speed
python main.py rosbag/1.bag /usv/001/scada/ctl/action/manual throttlePercent /usv/001/scada/ctl/action/pose rotateSpeed /usv/001/ctl/scada/action rudderPercent
 
[接口]
[/dataAnalysis/util/ get_all_info()方法] 获取所有topic以及对应的字段
---input [path]
---output数据示例
{'/usv/001/ctl/scada/route/detail': [{'id': 'string'}, {'name': 'string'}, {'version': 'int32'}, {'points': 'Point[]'}, {'obstacles': 'Point[]'}],
'/usv/001/scada/ctl/action/manual': [{'handleOk': 'int8'}, {'throttlePercent': 'int16'}, {'rudderPercent': 'int16'}], 
'/usv/001/scada/ctl/action/pose': [{'header': 'std_msgs/Header'}, {'lng': 'float64'}, {'lat': 'float64'}, {'high': 'float64'}, {'roll': 'float64'}, {'pitch': 'float64'}, {'yaw': 'float64'}, {'speed': 'float64'}, {'rotateSpeed': 'float64'}], 
'/usv/001/ctl/scada/action': [{'throttlePercent': 'int16'}, {'rudderPercent': 'int16'}], 
'/usv/001/ctl/nav/autoCommand': [{'workModel': 'int8'}, {'poseModel': 'int8'}, {'navRouteStartTime': 'float64'}], 
'/usv/001/ctl/scada/parameter/adjustList': [{'version': 'string'}, {'subVersion': 'string'}, {'data': 'Parameter[]'}], 
'/usv/001/ctl/scada/parameter/monitorList': [{'version': 'string'}, {'subVersion': 'string'}, {'data': 'Parameter[]'}], 
'/usv/001/ctl/scada/sensor/status': [{'gpsOk': 'int8'}, {'gpsSignal': 'int8'}, {'longitude': 'float64'}, {'latitude': 'float64'}, {'compassOk': 'int8'}, {'roll': 'int16'}, {'pitch': 'int16'}, {'lidarOk': 'int8'}], 
'/usv/001/ctl/scada/running/status': [{'workModel': 'int8'}, {'lostReturn': 'int8'}, {'speed': 'int16'}, {'heading': 'int16'}, {'leftThrottlePercent': 'int16'}, {'rightThrottlePercent': 'int16'}, {'leftRudder': 'int16'}, {'rightRudder': 'int16'}, {'thisRunTime': 'int16'}, {'totalRunTime': 'int32'}, {'safeStrategy': 'int8'}],
'/usv/001/ctl/scada/auto/status': [{'adviseSpeed': 'int16'}, {'adviseLeftThrottle': 'int16'}, {'adviseRightThrottle': 'int16'}, {'adviseHeading': 'int16'}, {'adviseLeftRudder': 'int16'}, {'adviseRightRudder': 'int16'}, {'avoidanceActivated': 'int8'}, {'leftAvoidanceAngle': 'int16'}, {'rightAvoidanceAngle': 'int16'}], 
'/usv/001/ctl/scada/communication/status': [{'fpvCameraOk': 'int8'}, {'boardOk': 'int8'}]}

即{'topic':[字段字典组成的列表]...}形式