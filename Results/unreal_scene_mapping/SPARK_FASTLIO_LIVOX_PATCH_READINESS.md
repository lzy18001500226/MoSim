# spark-fast-lio Livox Patch Readiness

- candidate: `Results/tmp/fastlio_ros2_candidates/spark-fast-lio/spark_fast_lio`
- ready: `true`
- decision: `ready_for_build_runtime_gate`
- next_action: Build the candidate and run headless MoSim Mid360 truth evaluation.

## Checks

| Status | Check | Reason |
|---|---|---|
| PASS | `candidate_tree_exists` | spark-fast-lio candidate source tree must exist under the ignored Results/tmp workspace. |
| PASS | `uses_ros2_livox_driver2_package` | ROS2 Humble Mid360 route should use livox_ros_driver2 package naming, not ROS1 livox_ros_driver. |
| PASS | `does_not_find_ros1_livox_driver` | CMake must not gate the ROS2 CustomMsg path on ROS1 livox_ros_driver. |
| PASS | `preprocess_uses_ros2_custommsg_header` | Preprocess header must include ROS2 livox_ros_driver2/msg/custom_msg.hpp. |
| PASS | `preprocess_drops_ros1_custommsg_header` | Preprocess header must not include ROS1 livox_ros_driver/CustomMsg.h in a ROS2 candidate. |
| PASS | `preprocess_signature_is_ros2_custommsg` | Preprocess process()/avia_handler() overloads must accept livox_ros_driver2::msg::CustomMsg. |
| PASS | `livox_macro_consistent` | The candidate currently has a typo-prone macro path; all guards should consistently use LIVOX_ROS_DRIVER_FOUND. |
| PASS | `livox_callback_binding_consistent` | Subscriber binding must match the declared livoxLiDARCallback symbol exactly. |
| PASS | `livox_callback_uses_member_imu_buffer` | Livox callback must use the class member imu_buffer_, not an undeclared imu_buffer. |
| PASS | `livox_callback_uses_nanoseconds` | rclcpp::Time exposes nanoseconds(); the typo nanseconds() blocks the CustomMsg path. |
| PASS | `pointcloud2_path_not_used_as_mid360_claim` | Mid360 evidence must go through a Livox-aware path, not only Ouster/Kimera/Velodyne PointCloud2 cases. |

## Claim Boundary

- Passing this static gate is not FAST-LIO localization evidence.
- Runtime evidence still requires nonzero registered cloud, odometry, path, coherent timestamps, and truth-error metrics.
