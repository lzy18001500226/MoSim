# Minimal ROS2 Livox CustomMsg schema used by FAST-LIO-family integrations.
# This mirrors the Livox/Sunray field contract needed for per-point timing.

std_msgs/Header header
uint64 timebase
uint32 point_num
uint8 lidar_id
uint8[3] rsvd
CustomPoint[] points
