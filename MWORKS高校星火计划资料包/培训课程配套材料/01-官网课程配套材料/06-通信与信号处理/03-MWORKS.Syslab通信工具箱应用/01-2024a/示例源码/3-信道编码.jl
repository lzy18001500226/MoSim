using TyCommunication
using TyMath
using TyBase
#示例1
# 为码字长度为 7 的汉明码生成校验矩阵H和生成矩阵G
H, G = hammgen(3)
#========================================================================#
#示例2
# 为 [7,4] 汉明码设置参数
m = 3
n = 2^m - 1
k = n - m
# 产生一个奇偶校验矩阵和解码表
parmat, = hammgen(m)
trt = syndtable(parmat)
# 指定一个接收数据的向量
recd = [1 0 0 1 1 1 1]
# 计算校验子，然后显示校验子的十进制和二进制值
syndrome = rem.(recd * parmat', 2)
syndrome_int = bi2de(syndrome, "left-msb")
println("Syndrome =  " * string(syndrome_int) * " decimal, " * string(syndrome) * " binary")
# 通过使用解码表和校验子确定校正向量
corrvect = trt[1+syndrome_int, :]
# 然后通过校正向量计算出校正后的码字
correctedcode = rem.(corrvect .+ vec(recd), 2)
#========================================================================#
#示例3
# 设置码字和消息长度 n 和 k
N = 15
K = 11
# 创建生成多项式并返回纠错能力 t
genpoly1, t = bchgenpoly(15, 11)
# 使用不同本原多项式为 (15,11) BCH 码创建生成多项式
genpoly2, = bchgenpoly(15, 11, 19) 
#========================================================================#
#示例4
# 计算 BCH 码字长度为 15 的可能消息长度组合
T1 = bchnumerr(15)
# 计算 BCH 码 15,11 的可纠正错误数
T2 = bchnumerr(15, 11) 
#========================================================================#
#示例5
# 为 GF(2) 的 Galois 数组设置 BCH 参数
rng = MT19937ar(1234)
M = 4
n = 2^M - 1
k = 5
nwords = 10
# 创建消息
msgTx = GF1.(randi(rng, [0 1], nwords, k))
# 查找纠错能力
t = bchnumerr(n, k)
# 对消息进行编码
enc = bchenc(msgTx, n, k)
# 每个码字中最多损坏 t 比特
noisycode = enc + GF1.(randerr(nwords, n, collect((1:t)')))
# 解码有噪声的码字
msgRx, = bchdec(noisycode, n, k)
# 验证消息是否已正确解码
println(isequal(msgTx, msgRx)) 
#========================================================================#
#示例5
rng = MT19937ar(1234)
# 使用 poly2trellis 函数定义用于配置编码器的 trellis 结构
trellis_a = poly2trellis([5 4], [23 35 0; 0 5 13])
# 使用 trellis_a 结构来配置 convenc 函数
K = log2(trellis_a.numInputSymbols)
N = log2(trellis_a.numOutputSymbols)
numReg = log2(trellis_a.numStates)
numSymPerFrame = 5
K = convert(Int64, K)
numSymPerFrame = convert(Int64, numSymPerFrame)
data = rand(rng, 0:1, K * numSymPerFrame)
# 以 2/3 的码率为五个二进制符号进行编码
code_a, fstate_a = convenc(data, trellis_a)
# 验证编码输出是否为 15 位，即输入序列数据长度的 3/2 (N/K) 倍
k = length(data) // length(code_a)
#========================================================================#
#示例6
Random.seed!(1234)
# 定义图中表示的卷积编码网格
trellis1 = poly2trellis([5 4], [23 35 0; 0 5 13])
K = log2(trellis1.numInputSymbols)
N = log2(trellis1.numOutputSymbols)
coderate = K / N
fprintf("K is %d and N is %d. The code rate is %3.2f\n", K, N, coderate)
# 设置调制顺序，并计算每个调制符号的比特数
M = 16
bps = log2(M)
numSymPerFrame = 5000
dataIn = randi([0 1], trunc(Int64, K * bps * numSymPerFrame), 1)
# 对输入数据进行卷积编码
codedout, = convenc(dataIn, trellis1)
#  对编码符号应用 16-QAM 调制
txSig = qammod(codedout, M, InputType="bit")
# 计算 awgn 函数使用的信噪比值
EbNo = 9
snr1 = EbNo + 10 * log10(bps * coderate)
# 通过AWGN信道
rxSig = awgn(txSig, snr1, "measured")
# 解调接收到的信号
demodSig = qamdemod(rxSig, M, OutputType="bit")
#  指定维特比解码器的回溯深度
tbdepth = 16
# 使用维特比解码器解码二进制解调信号
dataOut, = vitdec(demodSig, trellis1, tbdepth, "cont", "hard")
# 将编码的误码率与理论的未编码的误码率进行比较
decDelay = K * tbdepth
decDelay = trunc(Int64, decDelay)
berCoded = biterr(dataIn[1:end-decDelay], dataOut[decDelay+1:end]) ./ length(dataOut[decDelay+1:end])
length(dataOut[decDelay+1:end])
berUncoded = berawgn(EbNo, "qam", M)
fprintf("The coded BER is %6.5f\nThe uncoded BER is %6.5f\n", [berCoded[1] berUncoded[1]])
