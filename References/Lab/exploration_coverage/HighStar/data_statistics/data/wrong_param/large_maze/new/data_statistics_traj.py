import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

base_path = '/home/wzy/FSMP/src/FSMP-master/data_statistics/data/large_maze/'
folders = ['success_1', 'success_2', 'success_3', 'success_4', 'success_5']
all_y_data = []  # 存储所有文件的插值后的y数据
common_x = None  # 通用的x时间轴，将由最长的x轴定义

# 首先，找出最长的x轴时间点用于统一插值
max_length = 0
for folder in folders:
    traj_t_path = os.path.join(base_path, folder, 'traj_t.txt')
    with open(traj_t_path, 'r') as file:
        x_data = np.array([float(line.strip()) for line in file.readlines()])
        if len(x_data) > max_length:
            max_length = len(x_data)
            common_x = x_data

# 然后，对每个数据集进行插值
for folder in folders:
    traj_path = os.path.join(base_path, folder, 'traj.txt')
    traj_t_path = os.path.join(base_path, folder, 'traj_t.txt')

    with open(traj_path, 'r') as file:
        y_data = np.array([float(line.strip()) for line in file.readlines()])
    
    with open(traj_t_path, 'r') as file:
        x_data = np.array([float(line.strip()) for line in file.readlines()])
    
    # 创建插值函数
    f = interp1d(x_data, y_data, bounds_error=False, fill_value='extrapolate')
    # 插值到共同的x轴
    interpolated_y = f(common_x)
    all_y_data.append(interpolated_y)
    print(interpolated_y[200])

# 计算平均值
average_y = np.mean(all_y_data, axis=0)
# print(average_y[200])
# print(average_y[2000])

# 绘制曲线
plt.figure(figsize=(10, 5))
plt.plot(common_x, average_y, label='Average Trajectory', marker='o')
plt.xlabel('Time (t)')
plt.ylabel('Average Trajectory (x)')
plt.title('Average Trajectory vs Time')
plt.legend()
plt.grid(True)
plt.show()
