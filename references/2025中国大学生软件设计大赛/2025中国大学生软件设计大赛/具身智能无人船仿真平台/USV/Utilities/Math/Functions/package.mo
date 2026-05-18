package Functions "函数"
  annotation(__MWORKS(version="2025a"));
  function roundToNDecimal "四舍五入且保留n位小数"
    annotation(__MWORKS(version = "2025a"));
    input Real x;
    input Integer n;
    output Real result;
  algorithm
    result := floor(x * 10 ^ n + 0.5) / 10 ^ n;  // 乘10后四舍五入到整数，再除以10
  end roundToNDecimal;

end Functions;