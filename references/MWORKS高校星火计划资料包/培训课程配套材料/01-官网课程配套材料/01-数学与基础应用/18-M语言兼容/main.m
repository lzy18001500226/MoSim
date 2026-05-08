subs_sci;
%可直接访问全局变量
% 以前版本需要在每个脚本都声明需要的 global 变量
for i = nums
count = count + 1;
end
myfunc(count);
values
function myfunc(v)
%函数内需要声明用到的全局变量
%global values
values
values = v + values;
end