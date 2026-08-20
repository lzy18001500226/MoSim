import scipy.io as sio
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# 查找 MCP workspace 中的最新 .mat 文件
import os
import glob

mcp_workspace = r'D:\Program Files\MWORKS\Sysplorer 2026a\Tools\sysplorer_mcp'
mat_files = glob.glob(os.path.join(mcp_workspace, '*.mat'))

if not mat_files:
    # 尝试 MWORKS 文档目录
    mcp_workspace = r'C:\Users\HP\Documents\MWORKS'
    mat_files = glob.glob(os.path.join(mcp_workspace, '*.mat'))

if not mat_files:
    print(f'ERROR: No .mat files found in {mcp_workspace}')
    exit(1)

latest_mat = max(mat_files, key=os.path.getmtime)
print(f'Loading: {latest_mat}')

# 加载数据
data = sio.loadmat(latest_mat)
time = data['time'].flatten()
uav1_x = data['plant_1.position[1]'].flatten()
uav1_y = data['plant_1.position[2]'].flatten()
uav1_z = data['plant_1.position[3]'].flatten()
uav2_x = data['plant_2.position[1]'].flatten()
uav2_y = data['plant_2.position[2]'].flatten()
uav2_z = data['plant_2.position[3]'].flatten()
uav3_x = data['plant_3.position[1]'].flatten()
uav3_y = data['plant_3.position[2]'].flatten()
uav3_z = data['plant_3.position[3]'].flatten()

print(f'Time: {time[0]:.1f}~{time[-1]:.1f}s, {len(time)} points')

# 计算机间距离
dist_12 = np.sqrt((uav1_x - uav2_x)**2 + (uav1_y - uav2_y)**2 + (uav1_z - uav2_z)**2)
dist_13 = np.sqrt((uav1_x - uav3_x)**2 + (uav1_y - uav3_y)**2 + (uav1_z - uav3_z)**2)
dist_23 = np.sqrt((uav2_x - uav3_x)**2 + (uav2_y - uav3_y)**2 + (uav2_z - uav3_z)**2)
min_dist = min(dist_12.min(), dist_13.min(), dist_23.min())

print(f'\n最小机间距离: {min_dist:.3f} m')
print(f'  UAV1-UAV2: {dist_12.min():.3f} m')
print(f'  UAV1-UAV3: {dist_13.min():.3f} m')
print(f'  UAV2-UAV3: {dist_23.min():.3f} m')

# 绘制3D轨迹
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

ax.plot(uav1_x, uav1_y, uav1_z, 'r-', linewidth=2, label='UAV1', alpha=0.8)
ax.plot(uav2_x, uav2_y, uav2_z, 'g-', linewidth=2, label='UAV2', alpha=0.8)
ax.plot(uav3_x, uav3_y, uav3_z, 'b-', linewidth=2, label='UAV3', alpha=0.8)

ax.scatter(uav1_x[0], uav1_y[0], uav1_z[0], c='r', marker='o', s=100, label='起点')
ax.scatter([uav1_x[-1], uav2_x[-1], uav3_x[-1]],
           [uav1_y[-1], uav2_y[-1], uav3_y[-1]],
           [uav1_z[-1], uav2_z[-1], uav3_z[-1]],
           c=['darkred', 'darkgreen', 'darkblue'], marker='s', s=100, label='终点')

ax.set_xlabel('X (m)', fontsize=12)
ax.set_ylabel('Y (m)', fontsize=12)
ax.set_zlabel('Z (m)', fontsize=12)
ax.set_title('三机异构编队轨迹(OpenBlocks场景)', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

output = r'C:\Users\HP\Desktop\MoSim\Docs\报告\PPT\三机异构编队轨迹_OpenBlocks.png'
plt.savefig(output, dpi=300, bbox_inches='tight')
print(f'\n已保存: {output}')
plt.close()
