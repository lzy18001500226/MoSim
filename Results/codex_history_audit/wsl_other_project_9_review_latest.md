# WSL Other Project 9 Review

Read-only extract from `/home/linux/.codex`; no history modified. These are the 9 non-MoSim, non-DH, non-subagent records from the cleanup bucket.

## 1. gpu_test - 019e5312-f47c-7ab3-9b97-ca55b3d1c32f

- State: active
- Updated CST: 2026-06-03 12:06:52
- CWD: `/mnt/e/signal_processing/gpu_test`
- Source: `vscode` / thread_source=`user`
- Rollout: `/home/linux/.codex/sessions/2026/05/23/rollout-2026-05-23T12-23-31-019e5312-f47c-7ab3-9b97-ca55b3d1c32f.jsonl`
- User request:

```text
吞吐量逼近理论值、实现零丢包实时处理核心方案

先理清核心逻辑：理论吞吐量 = 硬件最大带宽/采样速率/总线极限，实际达不到一般是链路瓶颈、缓存调度、CPU/GPU算力抢占、拷贝开销、线程调度、IO阻塞、协议冗余导致。下面从底层到上层，给你可落地的优化路径，帮吞吐量对齐理论值、实现稳定实时处理。（查看实验报告可知我们总是与理论值有差距）

一、先明确理论吞吐量基准
当前场景：1MHz采样率、多通道、CUDA+RTX5080、.NET9、实时信号处理
理论吞吐量公式：
\text{理论吞吐量} = \text{单样本字节数} \times \text{采样率} \times \text{通道数}
先把理论上限算死，后续所有优化目标就是实测吞吐量无限贴近该值，无累积延迟、无丢包。
实时处理核心要求：单帧处理耗时 ≤ 单帧产生耗时，否则数据会堆积、延迟越来越大，最终丢包。

二、底层传输层优化（最影响吞吐量的核心）
1. 消除内存拷贝开销
这是.NET+CUDA场景最大损耗点
• 禁用用户态→内核态频繁拷贝，使用零拷贝
◦ CUDA：使用cudaHostAlloc分配锁页内存，避免系统页交换，CPU↔GPU直接DMA传输
◦ .NET：用UnmanagedMemoryAccessor、原生指针、Span无托管拷贝，杜绝托管堆频繁GC拷贝
• 统一内存架构（UMA）：开启CUDA Unified Memory，减少显式Memcpy次数，适合连续流式数据
2. 总线带宽打满
• PCIe链路：确认RTX5080跑在PCIe 4.0 x16满速，不要降速到x8/x4
• 避免多设备共享PCIe带宽，减少其他显卡、网卡、SSD抢占带宽
• 批量传输：小数据包合并成大块批量传输，减少传输中断、指令开销，流式数据不要逐样本传输
三、缓冲区架构优化（解决实时丢包、数据堆积）
实时处理必须用环形缓冲区（RingBuffer），拒绝普通队列，核心设计：
1. 双层缓冲/双缓冲Ping-Pong
一块缓冲区接收新数据，一块缓冲区交由GPU运算，读写完全并行，无等待阻塞
2. 环形缓冲区固定大小预分配
全程不动态扩容、不new内存，避免GC停顿、内存碎片

3. 分离生产者/消费者线程
◦ 生产者：硬件采集线程，只做数据写入环形缓冲，不做任何计算
◦ 消费者：CUDA处理线程，只取数据运算，不阻塞采集
4. 水位阈值控制
设置高低水位，低水位正常处理，高水位预警限流，防止缓冲区撑爆丢包
四、CUDA核函数与算力优化（榨满GPU理论算力）

1. 核函数并行粒度对齐硬件
◦ 线程块、线程数贴合SM流多处理器架构，避免线程空闲、资源浪费
◦ 多通道并行拆解，让GPU算力100%打满，无空闲周期
2. 减少核函数启停开销
批量提交核任务，不要单帧单次调用核函数，合并任务流
3. 复用GPU显存
预分配显存空间，全程复用，不频繁cudaMalloc/cudaFree
4. 避免CPU-GPU频繁同步
尽量异步执行：cudaStream异步流，CPU不用等待GPU计算完成再接收下一帧，实现流水并行
五、CPU侧&线程调度优化（.NET场景重点）
1. 线程优先级提升
采集线程、处理线程设置为高实时优先级，避免系统后台进程抢占CPU时间片
2. 禁用不必要GC
◦ .NET开启GC延迟模式、固定堆，减少GC STW停顿
◦ 全程使用非托管内存，减少托管对象创建
3. 绑定CPU亲和性
把采集线程绑定到指定物理核心，避免线程跨核心调度开销，减少缓存失效
4. 杜绝同步阻塞
全程用异步IO、无锁编程，用原子操作代替lock锁，锁竞争会直接拉低吞吐量、造成实时抖动
六、采样/采集侧链路优化（数据源端不拖后腿）

1. 硬件驱动使用高性能模式
关闭节能省电模式，网卡/采集卡跑满最高性能模式
2. 时钟同步对齐
采集采样时钟与处理时钟做同步，避免速率漂移导致数据堆积/丢包
3. 去除协议冗余
自定义传输协议精简头部，减少无效字节，提升有效数据吞吐量占比
七、实时性闭环校验：耗时约束
设单帧数据产生耗时为T_{in}，单帧处理耗时为T_{proc}
实现实时处理硬性条件：
T_{proc} \le T_{in}
同时保证：
传输耗时 + 计算耗时 + 拷贝耗时 < 帧间隔
只要满足该条件，吞吐量就能稳定跑满理论值，不会累积延迟、不会丢包。
八、调优落地步骤（按顺序排查，最快对齐理论值）

1. 先统计各环节耗时占比：采集、拷贝、CPU预处理、CUDA计算、数据输出，定位瓶颈点
2. 优先优化内存拷贝，实现零拷贝，收益最大
3. 改用环形缓冲+双缓冲架构，实现读写并行
4. 优化CUDA核函数与异步流，打满GPU算力
5. 优化.NET线程优先级、GC、CPU亲和性，消除系统抖动
6. 批量聚合数据，减少频繁传输调用
7. 压测长时间运行，观测吞吐量、延迟、丢包率，微调缓冲区大小

九、常见瓶颈对照
• 吞吐量远低于理论值、CPU占用高 → 托管拷贝过多、GC频繁、锁竞争
• 吞吐量偶尔达标、间歇性丢包 → 线程调度抖动、GC停顿、缓冲区过小
• GPU利用率低、吞吐量上不去 → 核函数并行度不足、频繁CPU-GPU同步
• 长时间运行延迟越来越大 → 处理耗时大于帧产生耗时，数据持续堆积

总体目标就是要实现真正的实时，零丢包，让吞吐量达到理论值，我给你的是我的方案，结合项目具体情况进行优化
```

## 2. gpu_test - 019e2f4c-fedb-75b1-807e-7a8ad37915ad

- State: active
- Updated CST: 2026-05-28 19:58:37
- CWD: `/mnt/e/signal_processing/gpu_test`
- Source: `vscode` / thread_source=`user`
- Rollout: `/home/linux/.codex/sessions/2026/05/16/rollout-2026-05-16T13-40-35-019e2f4c-fedb-75b1-807e-7a8ad37915ad.jsonl`
- User request:

```text
上次运行测试本项目，在256通道1MHz情况下的吞吐量是200MB/s，属于高速延迟状态，现在要进行优化，有以下分析：
目前流程大致是：
SDK数据 → Marshal.Copy → 环形缓冲区拷贝 → batchBuffer拷贝 → GPU输入重组 → cuFFT → 完整频谱拷回CPU → CPU计算峰值/RMS → 写summary文件

虽然 GPU 已经启用，错误码 5 已解决，但要冲 400 MB/s，现在这条链路里 CPU 拷贝次数太多，而且 FFT 结果仍然完整拷回 CPU 后再做摘要计算，这是主要瓶颈。

下一步优化方案：

1.加性能分段统计
统计 SDK 回调、缓冲写入、GPU H2D 拷贝、FFT、D2H 拷贝、CPU 摘要、文件写入各阶段耗时，先精确确认瓶颈。
2.异步写文件
summary 文件不要在处理线程里同步写，改成后台写入队列，避免磁盘 I/O 阻塞实时消费。
3.减少 CPU 拷贝
把当前多次 Array.Copy 改成块引用队列或 pinned buffer 池，减少 SDK 数据到 GPU 前的内存搬运。
4.GPU 端完成摘要计算
这是最关键一步。让 GPU 完成窗口函数、FFT 后峰值/RMS 归约，CPU 只接收每通道摘要结果，而不是接收完整频谱再扫描。
除了优化，我们还需要做一个具体的实验进行验证得到具体的指标，我们的最终目的是实现实时处理，硬性要求是达到400MB/s的吞吐量，这意味着我们至少要在400Mb/s的数据流情况下实现实时处理，无数据丢掉，所以我们不能总是拿最高的标准去测试吞吐量（256通道1MHz），可以慢慢地增加，去设计一个实验去测试，我现在开启的还是16*16通道，我们可以调整采样率，等得到具体的指标后，我可以再调整通道继续做实验得到指标
```

## 3. HP/Desktop - 019ddf78-e5f7-7b02-bcd9-35ddd016512e

- State: archived
- Updated CST: 2026-05-28 19:58:34
- CWD: `/mnt/c/users/hp/desktop`
- Source: `vscode` / thread_source=``
- Rollout: `/home/linux/.codex/archived_sessions/rollout-2026-05-01T01-38-55-019ddf78-e5f7-7b02-bcd9-35ddd016512e.jsonl`
- User request:

```text
你好
```

## 4. HP/Desktop - 019e39b0-979b-7940-8b1d-570f60202cd6

- State: archived
- Updated CST: 2026-05-28 19:58:30
- CWD: `/mnt/c/users/hp`
- Source: `cli` / thread_source=`user`
- Rollout: `/home/linux/.codex/archived_sessions/rollout-2026-05-18T14-05-35-019e39b0-979b-7940-8b1d-570f60202cd6.jsonl`
- User request:

```text
mcp
```

## 5. HP/Desktop - 019e39f9-7c27-7051-9958-131aa116b547

- State: archived
- Updated CST: 2026-05-28 19:58:29
- CWD: `/mnt/c/users/hp`
- Source: `cli` / thread_source=`user`
- Rollout: `/home/linux/.codex/archived_sessions/rollout-2026-05-18T15-25-12-019e39f9-7c27-7051-9958-131aa116b547.jsonl`
- User request:

```text
mcp
```

## 6. dog - 019e1aa8-5855-7c83-9db9-a97f1e1050e5

- State: archived
- Updated CST: 2026-05-28 12:36:49
- CWD: `/mnt/c/users/hp/desktop/dog`
- Source: `vscode` / thread_source=``
- Rollout: `/home/linux/.codex/archived_sessions/rollout-2026-05-12T13-28-20-019e1aa8-5855-7c83-9db9-a97f1e1050e5.jsonl`
- User request:

```text
给我生成一张小狗图片，这个是教程：https://github.com/router-for-me/CLIProxyAPI/commit/e935196df43cb9af478fea377571873d07c9a39b
```

## 7. jit-fine - 019e1f18-f11e-77a0-bcfa-00151b7133b4

- State: active
- Updated CST: 2026-05-18 00:15:41
- CWD: `/mnt/c/users/hp/desktop/jit-fine`
- Source: `vscode` / thread_source=``
- Rollout: `/home/linux/.codex/sessions/2026/05/13/rollout-2026-05-13T10-09-48-019e1f18-f11e-77a0-bcfa-00151b7133b4.jsonl`
- User request:

```text
新建一个conda环境叫jit
需要安装的依赖在：C:\Users\HP\Desktop\JIT-Fine\requirements.yml
```

## 8. gpu_test - 019e3478-40e6-7770-96f3-7e984002f5d1

- State: active
- Updated CST: 2026-05-17 16:09:58
- CWD: `/mnt/e/signal_processing/gpu_test`
- Source: `vscode` / thread_source=`user`
- Rollout: `/home/linux/.codex/sessions/2026/05/17/rollout-2026-05-17T13-45-56-019e3478-40e6-7770-96f3-7e984002f5d1.jsonl`
- User request:

```text
为什么回调不来数据，我给虚拟仪器设置的采样率是20wHz，为什么还显示1k？目标ip是192.168.1.119端口6000，设置都正确，它连接上虚拟仪器为什么调不过来数据？哪个没设置好？我代码本来好好的，给你改一下就成这样子

<image>
</image>
```

## 9. gpu_test - 019e344e-3c90-7722-878a-b8db0c7cc0d0

- State: active
- Updated CST: 2026-05-17 13:37:02
- CWD: `/mnt/e/signal_processing/gpu_test`
- Source: `vscode` / thread_source=`user`
- Rollout: `/home/linux/.codex/sessions/2026/05/17/rollout-2026-05-17T13-00-03-019e344e-3c90-7722-878a-b8db0c7cc0d0.jsonl`
- User request:

```text
代码里有一套让数据流流量递增实验的逻辑，但是昨天我回去看了一下 采样率确实不是我们代码能决定的，所以代码里面关于那套数据流递增的内容就无用了，可以删掉，我们现在需要做实验测试，只能选用甲方给的几个采样率 通道可以由我来调，它跑完数据你打开保存的数据就能知道采样率，我通过调采样率和通道，你这边启动程序跑一下，然后记录数据，跑一次，你记录一次，然后等我调参数，直到我说可以了，你就统计所有测试的数据再写实验报告，除了吞吐量，还要加入gpu占用率，现在做准备工作把，你改一下代码，我去配置通道和采样率
```
