using TyRobustControl
using TyControlSystems
using TyBase
using TyMath
using TyPlot

###############    第 2 章    ###############
# 示例 2.1：创建含有不确定实数和不确定复数的不确定矩阵
# 标称值为 5，变化范围为 [2,6] 的不确定实数
a = ureal("a",5,Range=[2,6]);
# 标称值为 1，变化率为 [-10%,10%] 的不确定实数
b = ureal("b",1,Percentage=10);
# 标称值为 3+4im，变化半径为 0.1 的不确定复数
c = ucomplex("c",3+4im,Radius=0.1);
# 不确定元素与确定元素拼接成不确定矩阵
M = [a b;b*a 7;c-a b^2];
a
b
c
get(M)
M.NominalValue

# --------------------------------------- #

# 示例 2.2：创建不确定状态空间模型
# 方法 1：基于不确定元素创建不确定模型
# 创建不确定元素
p1 = ureal("p1",10,Percentage=50); 
p2 = ureal("p2",3,PlusMinus=[-0.5,1.2]); 
# 创建不确定矩阵
A = [-p1 p2; 0 -p1]; 
B = [-p2; p2]; 
C = umat([1 0; 1 1]); 
D = umat([0; 0]);
# 创建不确定状态空间模型
usys = ss(A,B,C,D);
usys.NominalValue
usys.Uncertainty

# --------------------------------------- #

# 方法 2：直接将确定模型转化为不确定模型
# 创建状态空间模型
A = [-10 3; 0 -10]; 
B = [-3; 3]; 
C = [1 0; 1 1]; 
D = [0; 0];
sys = ss(A,B,C,D);
# 转化为对应的不确定模型
usys = uss(sys);
usys.NominalValue
usys.Uncertainty

###############    第 3 章    ###############
# 示例 3.1：计算MIMO反馈回路的盘稳定裕度
a = [0 10;-10 0]
b = eye(2)
c = [1 10;-10 1]
P = ss(a,b,c,0)
C = ss([1 -2;0 1])
Lo = P*C
# DMo 数组储存一次回路盘稳定裕度
# MMo 储存多次回路盘稳定裕度
DMo,MMo = diskmargin(Lo)
DMo[1]
DMo[2]
MMo

# --------------------------------------- #

# 示例 3.2：计算SISO系统的正规化左互质分解
sys = zpk([1 -1+2im -1-2im], [-1 2+1im 2-1im], 1);
fact, Ml, Nl = lncf(sys);
zpk(ss(Ml))
zpk(ss(Nl))
sigma(fact)

# --------------------------------------- #

# 示例 3.3：计算不确定矩阵的结构奇异值并提取附加信息
using Random
Random.seed!(0); 		# 固定随机数种子
M = randn(5,5) + im*randn(5,5); 
BlockStructure = [-1 0;-1 0;1 1;2 0];
Bounds, MuInfo = mussv(M,BlockStructure);
Bounds
propertynames(MuInfo)
MuInfo.bnds
MuInfo.blk
# 提取结构奇异值计算的附加信息
VDelta = mussvextract(MuInfo); 		# nargout 默认等于 1
_, VSigma = mussvextract(MuInfo;nargout=2);
_, _, VLmi = mussvextract(MuInfo;nargout=3);
VDelta
collect(keys(VSigma))
collect(keys(VLmi))

# --------------------------------------- #

# 示例 3.4：计算不确定系统的鲁棒稳定性裕度和鲁棒增益裕度
P = tf(1,[1 0]) + ultidyn("delta",[1,1],Bound=0.4);
BW = 0.8; 
K = tf(BW,[1/(25*BW) 1]); 
S = feedback(uss(1),P*K);
S
# 计算标称系统的峰值增益
gpeak,_ = getPeakGain(S.NominalValue);
gpeak
# 计算鲁棒稳定裕度与鲁棒增益裕度
stabmarg,_ = robstab(S);
perfmarg1,_ = robgain(S,1.05);   	# 相对于 1.05 的增益裕度
perfmarg2,_ = robgain(S,2); 	    # 相对于 2 的增益裕度
stabmarg
perfmarg1
perfmarg2

###############    第 4 章    ###############
# 示例 4.1：创建一阶连续时间加权函数
# 低频增益为 40 dB，高频增益滚降至 -20 dB，1 rad/s 时增益为 10 dB
Wl = makeweight(100,[1,3.16],0.1);
# 低频增益为 -10 dB，高频增益为 40 dB，交叉频率为 10 rad/s
Wh = makeweight(0.316,10,100);
# 绘制伯德图
bodemag(Wl,Wh)
legend(["Wl", "Wh"])
bodegrid(true)

# --------------------------------------- #

# 示例 4.2：创建高阶连续时间加权函数
# 低频增益为 -10 dB，高频增益为 40 dB，1 rad/s 时增益为 6 dB，阶数为 3
W3 = makeweight(0.316,[1,2],100,0,3);
# 低频/高频增益与 W3 相同，阶数为 1
W1 = makeweight(0.316,[1,2],100);
# 绘制伯德图，比较两者的区别
bodemag(W3,W1)
legend(["W3","W1"],loc="northwest")
bodegrid(true)

# --------------------------------------- #

# 示例 4.3：混合灵敏度问题求解
s = zpk('s');
G = (s-1)/(s+1)^2;
# W1 低频段增益为 20 dB，高频段增益 -40 dB，1 rad/s 时增益为 -20 dB
W1 = makeweight(10,[1,0.1],0.01);
# W2 低频段增益为 -20 dB，高频段增益 0 dB，32 rad/s 时增益为 -10 dB
W2 = makeweight(0.1,[32,0.32],1);
# W3 低频段增益 -40 dB，高频段增益 20 dB，1 rad/s 时增益为 -20 dB
W3 = makeweight(0.01,[1,0.1],10);
bodemag(W1,W2,W3)
# 计算控制器
K,CL,Gamma = mixsyn(G,W1,W2,W3);
Gamma
# 分析奇异值曲线
S = feedback(1,G*K);
KS = K*S;
T = 1-S;
sigma(S,"b",KS,"r",T,"g",Gamma/W1,"b-.",ss(Gamma/W2),"r-.",Gamma/W3,"g-.")
legend(["S","KS","T","GAM/W1","GAM/W2","GAM/W3"],loc="southwest")
bodegrid(true)

# --------------------------------------- #

# 示例 4.4：𝑯∞ 最优控制器
# 定义受控系统 G
s = zpk('s');
G = (s-1)/(s+1);
# 定义加权函数 W1,W2,W3
W1 = 0.1*(s+100)/(100*s+1); 
W2 = ss(0.1); 
W3 = nothing;
# 构造增广系统 P
P = augw(G,W1,W2,W3);
# 生成 𝐻∞ 稳定控制器
# 假设测量输出维度（B2的列数）为 1
Nmeas = 1;
# 假设控制输入维度（C2的行数）为 1
Ncon = 1;
K,CL,Gamma = hinfsyn(P,Nmeas,Ncon);
K
Gamma
# 检查闭环系统的奇异值图
sigma(CL,ss(Gamma))
legend(["CL","Gamma"])

# --------------------------------------- #

# 示例 4.5：生成 𝐻2 稳定控制器
# 被控对象定义
A = [5 6 -6;6 0 5;-6 5 4];
B = [0 4 0 0;1 1 -2 -2;4 0 0 -3];
C = [-6 0 8;0 5 0;-2 1 -4;4 -6 -5;0 -15 7];
D = [0 0 0 0;0 0 0 1;0 0 0 0;0 0 3 6;8 0 -7 0];
P = ss(A,B,C,D);
# 生成 𝐻2 最优稳定控制器
# 假设测量输出维度（B2 的列数）为 2
Nmeas = 2;
# 假设控制输入维度（C2 的行数）为 1
Ncon = 1;
K,CL,Gamma,Info = h2syn(P,Nmeas,Ncon);
K
Gamma
# 检验闭环系统的稳定性
pole(CL)

########## 第 5 章 ##########
# 示例 5.1：基于归一化互质分解方法计算 MIMO 系统的模型降阶
# 定义原系统
using Random
Random.seed!(0); 	# 固定随机数种子
G = rss(30,3,3);	# 30 阶随机系统
# 系统降阶
G1, _ = ncfmr(G,10);	# 10 阶降阶模型
G2, _ = ncfmr(G,20); 	# 20 阶降阶模型
sigma(G,G-G1,G-G2) 	# 比较近似误差

# --------------------------------------- #

# 示例 5.2：计算稳定/不稳定系统的 Hankel 奇异值
# 被控对象定义
G1 = tf(1,[1,5,6]); 		# 稳定系统
G2 = tf(1,[1,1,-6]); 		# 不稳定系统
# 直接计算 Hankel 奇异值
sv_stab1, sv_unstab1 = hankelsv(G1);	
sv_stab2, sv_unstab2 = hankelsv(G2); 
sv_stab1 
sv_unstab1
sv_stab2
sv_unstab2

# --------------------------------------- #

# 示例 5.3：系统模态形式实现与模态分解
A = [0 1 0 0;0 -0.1 3 0;0 0 0 1;0 -0.5 30 0];
B = [0; 2; 0; 5];
C = [1 0 0 0;0 0 1 0];
D = [0;0];
G = ss(A,B,C,D)
G1,G2 = modreal(G);
G1
G2
G1,G2 = modreal(G,2);
G1
G2

###############    第 6 章    ###############
# 示例 6.1：构造一个 LMI 系统
# 初始化 LMI 系统
hLMI = setlmis([]);
# 定义矩阵变量
X1, _, _ = lmivar(2,[3 3]);
X2, _, _ = lmivar(1,[3 1]);
x3, _, _ = lmivar(1,[1 1]);
# 定义常数矩阵
A = B = [1 2 3;4 5 6;7 8 9];
C = D = [1 2 3;0 1 0;3 2 1];
E = eye(3);
M = 2 * eye(6);
f = 3;
# 定义新的LMI
nlmi = newlmi()
# 定义LMI不等号左侧的项
lmiterm([nlmi,1,1,X2],2*A,A')  # 2*A*X2*A'
lmiterm([nlmi,1,1,x3],-1,E)    # -x3*E
lmiterm([nlmi,1,1,0],D*D')     # D*D' 
lmiterm([nlmi,2,1,-X1],1,B)    # X1'*B
lmiterm([nlmi,2,2,0],-1)       # -I
# 定义LMI不等号右侧的项
lmiterm([-nlmi,0,0,0],M)          # 外因子 M
lmiterm([-nlmi,1,1,X1],C,C',:s)   # C*X1*C'+C*X1'*C' 
lmiterm([-nlmi,2,2,X2],-f,1)      # -f*X2
# 获取LMI内部描述
lmisys = getlmis()