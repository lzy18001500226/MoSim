%从 MATLAB 中运行 Python 语句
pyrun("import localModule")
out = pyrun(["m= localModule.mvar","localModule.myFunc()"],"m")
%从 MATLAB 运行 Python 脚本文件
res = pyrunfile("addac.py","z","x",3,"y",2)
%为 Python 函数创建关键字参量
py.complex(pyargs('real',1,'imag',2))