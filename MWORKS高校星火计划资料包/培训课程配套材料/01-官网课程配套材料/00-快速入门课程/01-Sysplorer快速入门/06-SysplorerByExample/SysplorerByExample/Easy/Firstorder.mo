model Firstorder"简单一阶"
Real x(start=2,fixed=true)"变量x";
initial equation
x=3;
equation
der(x)=1-x;
end Firstorder;