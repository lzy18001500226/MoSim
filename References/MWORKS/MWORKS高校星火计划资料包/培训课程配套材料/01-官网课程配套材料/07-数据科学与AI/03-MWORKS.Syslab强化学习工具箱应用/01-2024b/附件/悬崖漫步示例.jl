using TyReinforcementLearning
# 创建环境
env = BuildEnv("CliffWalking-v0")

# 创建智能体模型
models = rlQLModels(
    Qtable=zeros(StateDims(env), ActionDims(env)));

# 创建智能体选项
option = rlQLAgentOptions(
    stateNum=StateDims(env),
    actionNum=ActionDims(env))

# 创建智能体对象
agent = rlQLAgent(models, option);

# 创建智能体训练选项
train_options = rlTrainOptions(
    max_episodes=1000,
    learning_interval=1,
    path=joinpath(pwd(), "result"));

# 执行训练
result = train!(agent, env, train_options)

# 结果展示
env = BuildEnv("CliffWalking-v0", true)
opt = rlSimulationOptions(numSimulations=3)
rlSim(agent, env, opt)
CloseEnv(env)
