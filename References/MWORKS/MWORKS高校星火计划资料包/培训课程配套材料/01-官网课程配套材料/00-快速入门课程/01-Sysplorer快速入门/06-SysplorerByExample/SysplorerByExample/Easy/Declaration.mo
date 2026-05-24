model Declaration "前缀的使用"
  annotation(__MWORKS(version = "2025b"));
  parameter Real R = 100 "电阻";         // 参数
  constant Real k = 1.380649e-23 "玻尔兹曼常数";  // 常量,不可更改
  input Real u "输入";            // 输入，常用在函数内
  output Real y "输出";          // 输出，常用在函数内
  Real v = 10 "内部电压";                     // 普通变量
  flow Real i = 1 "电流";                    // 流变量,满足“和为零”规则的变量
protected
  Real power;  // 内部计算的功率
  discrete Real count(start = 0);  // 仅在事件中更新
equation
  y = k * u;
  power = v * i;
  when sample(0, 1) then
    // 'pre(count)' 是一个特殊的操作符，用于获取事件发生“前一瞬间”的变量值。
    // 这条方程的含义是：在事件发生的瞬间，将 count 的新值设置为它之前的值加 1。
    count = pre(count) + 1;
  end when;
end Declaration;