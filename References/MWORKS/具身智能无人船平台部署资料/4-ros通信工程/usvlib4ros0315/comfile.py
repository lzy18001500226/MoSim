"""
异步订阅和发布话题在 usvlib4ros/usvRosUtil/usv_ros_topic.py 文件的 RosTopicProxy。topicHandler() 中添加
"""
from usvlib4ros import USVRosbridgeClient, RosTopicProxy, USVAutoNavigationService, GlobalData, USV_ROS_STSTUS
import time

"""
**************
1. ros 相关
"""
deviceId = "f697eb248e9354d0a725f6d4dd0a160c8a489aa1"

first = 0
def init(u):
	"""
	:return: 返回ros bridge 连接状态
	"""
	global first
	if first == 0:
		first = 1
		"""
		第一步：模型刚启动
		创建本地数据对象，
		启动 ros bridge tcp 线程
		"""
		# 获取当前目录
		import os,sys
		current_directory = os.getcwd()
		# print(current_directory)
		# 将当前目录添加到 sys.path
		if current_directory not in sys.path:
			sys.path.append(current_directory)

		from usvlib4ros import USVRosbridgeClient, RosTopicProxy, USVAutoNavigationService, GlobalData, USV_ROS_STSTUS,RosSrvClientProxy

		GlobalData.getInstance()
		USVRosbridgeClient.initRoslibpyLogger()
		USVRosbridgeClient.initUSVRosBridgeConnection("120.46.175.198", 8236)
		#USVRosbridgeClient.initUSVRosBridgeConnection("121.41.106.238", 8236)
		# USVRosbridgeClient.initUSVRosBridgeConnection("192.168.3.35", 9090)
		RosTopicProxy.firstConnectHandler(deviceId)
		RosTopicProxy.startService()
		RosSrvClientProxy.setDeviceId(deviceId)
		USVAutoNavigationService.getInstance().registerParameter()
		GlobalData.getInstance().ros_state = USV_ROS_STSTUS.INIT

	from usvlib4ros import USVRosbridgeClient,GlobalData,USV_ROS_STSTUS
	connected = USVRosbridgeClient.isRosConnected()
	ros_state = GlobalData.getInstance().ros_state

	if connected is True and ros_state == USV_ROS_STSTUS.INIT:
		"""
		第二步：ros bridge tcp 第一次连接成功
		异步启动 订阅话题、发布话题
		注册算法可调参数
		执行其他第一次ros连接成功后需要初始化的任务
		"""
		from usvlib4ros import USVAutoNavigationService, USVRosbridgeClient,RosTopicProxy

		GlobalData.getInstance().ros_state = USV_ROS_STSTUS.FIRST_CONNECTED

	elif ros_state == USV_ROS_STSTUS.FIRST_CONNECTED:
		"""
		ros 相关初始化已全部完成
		设置ros_state 为初始化完成，可以开始正常工作
		"""
		GlobalData.getInstance().ros_state = USV_ROS_STSTUS.INIT_FINISH

	import os

	return u,os.getpid()

"""
************
2. 船模型相关
"""

def getModelParams(u):
	from usvlib4ros import GlobalData
	return GlobalData.getInstance().modelParams


def getModelCommand(u):
	"""
	船模型输入
	adviseThrottlePercent = 0.0  # 建议油门百分比【-100~100】
	adviseRudderPercent = 0.0  # 建议方向百分比【-100~100】
	realSpeedX = 0.0  # 扰动速度z
	realSpeedY = 0.0  # 扰动速度y
	realSpeedZ = 0.0  # 扰动速度x
	"""
	from usvlib4ros import GlobalData
	modelCommand = GlobalData.getInstance().modelCommand
	adviseThrottlePercent = modelCommand.adviseThrottlePercent
	adviseRudderPercent = modelCommand.adviseRudderPercent
	realSpeedX = modelCommand.realSpeedX
	realSpeedY = modelCommand.realSpeedY
	realSpeedZ = modelCommand.realSpeedZ
	return adviseThrottlePercent,adviseRudderPercent,realSpeedX,realSpeedY,realSpeedZ

# modelReplyRostopic = None
# def setModelReply(u,finalSpeedX,finalSpeedY,finalYaw,params):
#    """
#    船模型输出
#    finalSpeedX                      --前进速度
#     finalSpeedY                      --横向速度
#     finalYaw                         --转向角速度
#     params                         --模型参数
#    """
#    import os
#    from usvlib4ros import GlobalData,USVRosbridgeClient
#    global modelReplyRostopic
#    if modelReplyRostopic is None and u > 10:
#       modelReplyRostopic = USVRosbridgeClient()

#    if modelReplyRostopic is not None:
#       msg = GlobalData.getInstance().modelReply.update(finalSpeedX,finalSpeedY,finalYaw,params)
#       modelReplyRostopic.publisherOnce(topicName="/usv/001/scada/model/command/reply",
#                                                msgName="message_pkg/ModelReply", topicMsg=msg)

#    """测试数据"""
#    return os.getpid()

modelReplyRostopic = None
def setModelReply(u,finalSpeedX,finalSpeedY,finalYaw,params):
	"""
	船模型输出
	finalSpeedX                      --前进速度
    finalSpeedY                      --横向速度
    finalYaw                         --转向角速度
    params                         --模型参数
	"""
	
	from usvlib4ros import GlobalData,USVRosbridgeClient
	global modelReplyRostopic
	if modelReplyRostopic is None:
		modelReplyRostopic = USVRosbridgeClient()
	if modelReplyRostopic is not None:
		msg = GlobalData.getInstance().modelReply.update(finalSpeedX,finalSpeedY,finalYaw,params)
		modelReplyRostopic.publisherOnce(topicName="usv/%s/scada/model/command/reply"%(deviceId),msgName = "message_pkg/ModelReply", topicMsg = msg)
	"""测试数据"""
	GlobalData.getInstance().modelReply.update(finalSpeedX,finalSpeedY,finalYaw,params)
	import os
	return os.getpid()

"""
************
3. 导航算法相关
"""

def routePlane(u):
	from usvlib4ros import USVAutoNavigationService,GlobalData,RoutePlanService,Constants

	if GlobalData.getInstance().routeUpdateFlag is True:
		"""路线已更新"""
		# route = GlobalData.getInstance().consumerRoute()
		# USVAutoNavigationService.getInstance().routePlaneService.reset(route=route)
		route = GlobalData.getInstance().consumerRoute()
		routeMeta = GlobalData.getInstance().routeMeta
		routeMeta.id = route.id
		routeMeta.name = route.name
		routeMeta.version = route.version
		routeMeta.write()

		USVAutoNavigationService.getInstance().routePlaneService.reset(route=route)

	"""获取模式和船位置"""
	workModel = GlobalData.getInstance().autoCommand.workModel
	isReturn = workModel == Constants.WorkMode.AutoReturn
	lng = GlobalData.getInstance().pose.lng
	lat = GlobalData.getInstance().pose.lat

	"""路径规划"""
	valid,nextPointIndex,destLng,destLat,prevLng,prevLat,shipToRouteDistance,shipToNextWPDistance,shipToPrevWPDistance = \
		USVAutoNavigationService.getInstance().routePlaneService.setCurrentPos(lng,lat,isReturn)

	return u,workModel,valid,nextPointIndex,destLng,destLat,prevLng,prevLat,shipToPrevWPDistance,shipToNextWPDistance,shipToRouteDistance

def getShipStatus(u):
	lng = GlobalData.getInstance().pose.lng
	lat = GlobalData.getInstance().pose.lat
	heading = GlobalData.getInstance().pose.yaw
	if heading > 180:
		heading = heading - 360
	realSpeed = GlobalData.getInstance().pose.speed
	realRotateSpeed = GlobalData.getInstance().pose.rotateSpeed
	return u,lng,lat,realSpeed,realRotateSpeed,heading

def navigation(u,workModel,lng,lat,realSpeed,realRotateSpeed,heading,valid ,destLng,destLat,prevLng,prevLat,shipToPrevWPDistance,shipToNextWPDistance,shipToRouteDistance):
	from usvlib4ros import USVAutoNavigationService,GlobalData,RoutePlanService,Constants
	global ros_state
	"""通过 prevPoint，destPoint，ship位置计算建议速度和角速度"""
	adviseSpeed, adviseRotate, advisedHeading = 0,0,0
	if valid is True and GlobalData.getInstance().ros_state == USV_ROS_STSTUS.INIT_FINISH :
		adviseSpeed,adviseRotate,advisedHeading = USVAutoNavigationService.getInstance().autoPilotService.setConditions(realSpeed, heading, lng, lat, destLng, destLat, prevLng, prevLat,
										shipToPrevWPDistance, shipToNextWPDistance, shipToRouteDistance)
	return u,adviseSpeed,adviseRotate,advisedHeading

def getDataFromRos(u):
	#unity ros data => sysplorer
	from usvlib4ros import GlobalData,Pose
	pose = GlobalData.getInstance().pose
	lng ,lat,speed,rotateSpeed,heading = pose.lng, pose.lat,pose.speed,pose.rotateSpeed,pose.yaw
	return u,lng,lat,speed,rotateSpeed,heading


def setDataToRos(u,adviseSpeed,adviseRotate,advisedHeading,nextPointIndex,shipToNextWPDistance):
	from usvlib4ros import GlobalData, AutoStatus
	GlobalData.getInstance().autoStatus.updateAutoStatus(adviseSpeed, adviseRotate, advisedHeading, nextPointIndex,
														 shipToNextWPDistance)
	return u

if __name__ == "__main__":
	u = 0.0
	from usvlib4ros import GlobalData
	import time
	while True:
		#ROS
		u,pid = init(u)

		u,workModel,valid,nextPointIndex,destLng,destLat,prevLng,prevLat,shipToPrevWPDistance,shipToNextWPDistance,shipToRouteDistance = routePlane(u)

		u,lng,lat,realSpeed,realRotateSpeed,heading = getShipStatus(u)

		u, adviseSpeed, adviseRotate, advisedHeading = navigation(u,workModel,lng,lat,realSpeed,realRotateSpeed,heading,valid ,destLng,destLat,prevLng,prevLat,shipToPrevWPDistance,shipToNextWPDistance,shipToRouteDistance)
		print(adviseSpeed, adviseRotate)
		# setDataToRos(u,adviseSpeed,adviseRotate,advisedHeading,nextPointIndex,shipToNextWPDistance)
		setDataToRos(u, adviseSpeed, adviseRotate, advisedHeading, nextPointIndex, shipToNextWPDistance)

		u,lng,lat,speed,rotateSpeed,heading = getDataFromRos(u)
		print(speed,rotateSpeed)
		getModelCommand(u)
		params = getModelParams(u)
		# params[12] = u #测试数据
		setModelReply(u, speed, speed, 0, params)


		print(params)
		time.sleep(0.1)
		u = u + 0.1
	pass





