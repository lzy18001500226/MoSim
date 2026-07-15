cmake_minimum_required(VERSION 2.8.3)
project(ato_test)

find_package(catkin_simple REQUIRED)
add_definitions(-std=c++14)

catkin_simple()

# cs_add_executable(fov_ray_test src/fov_ray_test.cpp)

# target_link_libraries(fov_ray_test
#     ${catkin_LIBRARIES})


# cs_add_executable(swarm_data_test src/swarm_data_test.cpp)

# target_link_libraries(swarm_data_test
#     ${catkin_LIBRARIES})

# cs_add_executable(traj_swarm src/traj_swarm.cpp)

# target_link_libraries(traj_swarm
#         ${catkin_LIBRARIES})

# cs_add_executable(cmd_test src/cmd_test.cpp)

# target_link_libraries(cmd_test
#         ${catkin_LIBRARIES})

# cs_add_executable(cmd_repub src/cmd_repub.cpp)

# target_link_libraries(cmd_repub
#         ${catkin_LIBRARIES})

# cs_add_executable(GMM_test src/GMM_test.cpp)

# target_link_libraries(cmd_repub
#         ${catkin_LIBRARIES})

cs_add_executable(init_traj_test src/init_traj_test.cpp)

target_link_libraries(init_traj_test
        ${catkin_LIBRARIES})

# cs_add_executable(traj_plan src/traj_plan.cpp)

# target_link_libraries(traj_plan
#         ${catkin_LIBRARIES})

cs_add_executable(hull_test src/hull_test.cpp)

target_link_libraries(hull_test
        ${catkin_LIBRARIES})

cs_add_executable(map_test src/map_test.cpp)

target_link_libraries(map_test
        ${catkin_LIBRARIES})

cs_add_executable(traj_gain_test src/traj_gain_test.cpp)

target_link_libraries(traj_gain_test
        ${catkin_LIBRARIES})

cs_add_executable(traj_exc_run src/traj_exc_run.cpp)

target_link_libraries(traj_exc_run
        ${catkin_LIBRARIES})

cs_add_executable(vel_vis src/traj_vel_vis.cpp)

target_link_libraries(vel_vis
        ${catkin_LIBRARIES})# ${PROJECT_NAME})

cs_add_executable(odom_exc src/odom_exc.cpp)

target_link_libraries(odom_exc
        ${catkin_LIBRARIES})

cs_add_executable(energy_consumption src/energy_consumption.cpp)

target_link_libraries(energy_consumption
        ${catkin_LIBRARIES})
cs_install()
cs_export()