impure function random "生成(-1,1)之间的随机数"
  extends Modelica.Icons.Function;

  // 输入参数（可选：随机种子）
  input Integer seed "随机种子（用于初始化随机数生成器）";

  // 输出参数
  output Real randomValue "(-1,1)之间的随机数";

protected
  // 状态变量，用于随机数生成器
  Modelica.Math.Random.Utilities.randomState randomState;
  Real uniformRandom "标准化到[0,1]的随机数";

algorithm
  // 初始化随机数生成器状态
  randomState := Modelica.Math.Random.Utilities.initializeImpureRandom(seed);

  // 调用非纯函数生成随机数
  uniformRandom := Modelica.Math.Random.Utilities.impureRandom(randomState);

  // 映射到范围 (-1, 1)
  randomValue := 2 * uniformRandom - 1;
end random;