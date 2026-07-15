import os
import numpy as np
import matplotlib.pyplot as plt

# 文件夹路径
base_path = "/home/wzy/FSMP/src/FSMP-master/data_statistics/data/wrong_param/small_maze"
folders = ["success_1", "success_2", "success_3", "success_5"]

# 存储所有数据的列表
all_traj_data = []
all_traj_t_data = []

# 遍历每个文件夹和文件
max_length = 0
for folder in folders:
    traj_file_path = os.path.join(base_path, folder, "volume.txt")
    traj_t_file_path = os.path.join(base_path, folder, "volume_t.txt")
    
    with open(traj_file_path, 'r') as traj_file, open(traj_t_file_path, 'r') as traj_t_file:
        # 读取每个文件的数据，假设每行一个数据点
        traj_data = np.array([float(line.strip()) for line in traj_file])
        traj_t_data = np.array([float(line.strip()) for line in traj_t_file])
        
        all_traj_data.append(traj_data)
        all_traj_t_data.append(traj_t_data)
        
        if traj_data.size > max_length:
            max_length = traj_data.size

# 为了处理长度不一致，我们需要将所有数组填充到相同长度
uniform_traj_data = []
uniform_traj_t_data = []
for traj_data, traj_t_data in zip(all_traj_data, all_traj_t_data):
    if traj_data.size < max_length:
        padded_traj_data = np.pad(traj_data, (0, max_length - traj_data.size), mode='edge')
        padded_traj_t_data = np.pad(traj_t_data, (0, max_length - traj_t_data.size), mode='edge')
    else:
        padded_traj_data = traj_data
        padded_traj_t_data = traj_t_data

    uniform_traj_data.append(padded_traj_data)
    uniform_traj_t_data.append(padded_traj_t_data)

# 将列表转换为NumPy数组
traj_array = np.stack(uniform_traj_data)
traj_t_array = np.stack(uniform_traj_t_data)

# 计算每个索引的平均值
mean_traj_values = np.mean(traj_array, axis=0)
mean_traj_t_values = np.mean(traj_t_array, axis=0)

# 计算标准偏差
std_traj_deviation = np.std(traj_array, axis=0)

# 绘图
plt.figure(figsize=(10, 5))
plt.plot(mean_traj_t_values, mean_traj_values, linestyle='-', color='b')
plt.fill_between(mean_traj_t_values, mean_traj_values - std_traj_deviation, mean_traj_values + std_traj_deviation, color='b', alpha=0.2)
plt.title('Trajectory Value vs. Time with Variance Band')
plt.xlabel('Time')
plt.ylabel('Trajectory Value')
plt.grid(True)
plt.show()

