% 文件1
function [result,absResult] = addme2(a,b)
    result = a+b
    if nargout > 1
        absResult = abs(result);
    end
end
% 文件2 或 在命令行窗口输入
addme2(1,-3)
% 返回 -2
[x,y]=addme2(1,-3)
% x = -2, y = 2



