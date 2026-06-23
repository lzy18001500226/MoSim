cmake_minimum_required(VERSION 3.8)
project(mosim_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ControllerOutput.msg"
  "msg/PositionCommand.msg"
  "msg/PlannerSetpoint.msg"
  "msg/SetpointAdapterStatus.msg"
  DEPENDENCIES geometry_msgs std_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
