#!/bin/bash

# tmux版本的Astar仿真启动脚本
# 每个ROS节点在单独的tmux窗口中运行

SESSION_NAME="astar_simulation"

# 清理函数 - 关闭所有相关的tmux会话
cleanup() {
    echo "正在关闭 tmux 会话..."
    tmux kill-session -t $SESSION_NAME 2>/dev/null || true
    echo "清理完成"
    exit 0
}

# 捕获信号以进行清理
trap cleanup SIGINT SIGTERM

# 检查tmux是否已安装
if ! command -v tmux &> /dev/null; then
    echo "错误: tmux 未安装。请先安装 tmux: sudo apt install tmux"
    exit 1
fi

# 如果会话已存在，先关闭它
tmux has-session -t $SESSION_NAME 2>/dev/null && tmux kill-session -t $SESSION_NAME

echo "创建 tmux 会话: $SESSION_NAME"

# 创建新的tmux会话，第一个窗口用于roscore
tmux new-session -d -s $SESSION_NAME -n "roscore"
tmux send-keys -t $SESSION_NAME:roscore "echo '启动 roscore...'" C-m
tmux send-keys -t $SESSION_NAME:roscore "roscore" C-m
echo "roscore 已在窗口 'roscore' 中启动"
sleep 5

# 创建窗口并启动仿真器
tmux new-window -t $SESSION_NAME -n "simulator"
tmux send-keys -t $SESSION_NAME:simulator "echo '启动仿真器...'" C-m
tmux send-keys -t $SESSION_NAME:simulator "roslaunch sunray_simulator sunray_sim_2025competiton.launch" C-m
echo "仿真器已在窗口 'simulator' 中启动"
sleep 5

# 创建窗口并启动publisher
tmux new-window -t $SESSION_NAME -n "publisher"
tmux send-keys -t $SESSION_NAME:publisher "echo '启动 publisher...'" C-m
tmux send-keys -t $SESSION_NAME:publisher "roslaunch 2025_uav_competiton_demo position_pub.launch" C-m
echo "publisher 已在窗口 'publisher' 中启动"
sleep 2

# 创建窗口并启动fusion
tmux new-window -t $SESSION_NAME -n "fusion"
tmux send-keys -t $SESSION_NAME:fusion "echo '启动 fusion...'" C-m
tmux send-keys -t $SESSION_NAME:fusion "roslaunch sunray_uav_control external_fusion.launch external_source:=2 enable_rviz:=false" C-m
echo "fusion 已在窗口 'fusion' 中启动"
sleep 2

# 创建窗口并启动control
tmux new-window -t $SESSION_NAME -n "control"
tmux send-keys -t $SESSION_NAME:control "echo '启动 control...'" C-m
tmux send-keys -t $SESSION_NAME:control "roslaunch sunray_uav_control sunray_control_node.launch uav_id:=1" C-m
echo "control 已在窗口 'control' 中启动"
sleep 2

# 创建窗口并启动demo
tmux new-window -t $SESSION_NAME -n "astar_demo"
tmux send-keys -t $SESSION_NAME:astar_demo "echo '启动 Astar demo...'" C-m
tmux send-keys -t $SESSION_NAME:astar_demo "roslaunch 2025_uav_competiton_demo Astar.launch enable_rviz:=true sim:=true" C-m
echo "Astar demo 已在窗口 'astar_demo' 中启动"
sleep 1

# 创建一个监控窗口
tmux new-window -t $SESSION_NAME -n "monitor"
tmux send-keys -t $SESSION_NAME:monitor "echo '监控窗口 - 可以在这里运行 rostopic list, rqt_graph 等命令'" C-m
tmux send-keys -t $SESSION_NAME:monitor "echo '使用以下命令在窗口间切换:'" C-m
tmux send-keys -t $SESSION_NAME:monitor "echo '  Ctrl+b + 0-6: 切换到对应编号的窗口'" C-m
tmux send-keys -t $SESSION_NAME:monitor "echo '  Ctrl+b + n: 下一个窗口'" C-m
tmux send-keys -t $SESSION_NAME:monitor "echo '  Ctrl+b + p: 上一个窗口'" C-m
tmux send-keys -t $SESSION_NAME:monitor "echo '  Ctrl+b + l: 最后使用的窗口'" C-m
tmux send-keys -t $SESSION_NAME:monitor "echo '退出整个仿真: Ctrl+C 或运行 tmux kill-session -t $SESSION_NAME'" C-m

echo ""
echo "========================================"
echo "所有节点已启动完成！"
echo "tmux 会话名称: $SESSION_NAME"
echo "窗口列表:"
echo "  0: roscore"
echo "  1: simulator"
echo "  2: publisher" 
echo "  3: fusion"
echo "  4: control"
echo "  5: astar_demo"
echo "  6: monitor (当前)"
echo ""
echo "快捷键:"
echo "  Ctrl+b + 数字键: 切换窗口"
echo "  Ctrl+b + d: 分离会话(保持后台运行)"
echo "  Ctrl+C: 中止脚本(会话继续运行)"
echo ""
echo "要重新连接会话，使用: tmux attach -t $SESSION_NAME"
echo "要完全关闭仿真，使用: tmux kill-session -t $SESSION_NAME"
echo "========================================"

# 连接到tmux会话，默认显示监控窗口
tmux attach -t $SESSION_NAME
