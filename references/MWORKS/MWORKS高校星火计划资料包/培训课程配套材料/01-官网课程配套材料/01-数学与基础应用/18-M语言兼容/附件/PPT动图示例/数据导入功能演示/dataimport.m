clc,clear, close all;
%% 加载文件中的语音数据并播放
% 加载语音数据文件并画图

% 显示语音信号
Fs = 8192;  % 固定采样率

% 播放语音
soundsc(u0_speech, Fs);
