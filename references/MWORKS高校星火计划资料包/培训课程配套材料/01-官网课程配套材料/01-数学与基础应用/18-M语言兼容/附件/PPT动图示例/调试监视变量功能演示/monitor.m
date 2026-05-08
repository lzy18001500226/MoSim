%% 信号处理脚本
clc; clear; close all;
rng default
% 1. 定义关键参数（新增：明确设置采样频率fs）
fs = 100;                  % 采样频率 (Hz) - 关键修正点
duration = 10;             % 信号持续时间 (秒)
t = 0:1/fs:duration;       % 时间向量（基于fs生成）

% 2. 生成测试信号（确保与fs匹配）
signal = sin(2*pi*1*t) + 0.5*randn(size(t)); % 1Hz正弦波+噪声

% 3. 计算初始统计量（调试监视表达式）
raw_mean = mean(signal);    % 原始信号均值
raw_noise = std(signal);    % 原始信号噪声水平
disp(['原始信号: 均值=', num2str(raw_mean), ', 噪声标准差=', num2str(raw_noise)]);

% 4. 设计滤波器（关键修正：确保cutoff_freq < fs/2）
cutoff_freq = 2;           % 截止频率 (Hz)
if cutoff_freq >= fs/2
    error('截止频率必须小于奈奎斯特频率(fs/2=%.1fHz)', fs/2);
end
[b, a] = butter(4, cutoff_freq/(fs/2), 'low'); % 4阶低通滤波器

% 5. 应用滤波器
filtered_signal = filtfilt(b, a, signal); % 零相位滤波

% 6. 计算滤波后统计量
filtered_mean = mean(filtered_signal);
filtered_noise = std(filtered_signal);
disp(['滤波后信号: 均值=', num2str(filtered_mean), ', 噪声标准差=', num2str(filtered_noise)]);









% 7. 可视化结果（含频域分析）
figure('Color', 'white', 'Position', [100,100,800,600]);

% 时域图
% subplot(2,1,1);
plot(t, signal, 'b-', 'LineWidth', 0.8); hold on;
plot(t, filtered_signal, 'r--', 'LineWidth', 1.5);
xlim([0, 2]); % 只显示前2秒便于观察
title('时域信号对比');
xlabel('时间 (s)');
ylabel('幅值');
legend('原始信号', '滤波后信号', 'Location', 'northeast');
grid on;
