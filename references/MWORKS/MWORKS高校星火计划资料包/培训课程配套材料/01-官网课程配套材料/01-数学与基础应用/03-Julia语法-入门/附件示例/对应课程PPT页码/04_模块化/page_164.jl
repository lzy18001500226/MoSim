module A
export f
f() = 1
end

module B
export f
f() = 2
end

using .A, .B # 同时导入模块 A 和 B
f()
# WARNING: both B and A export "f"; uses of it in module Main must be qualified
# ERROR: UndefVarError: `f` not defined

using .A: f as f;
f()
# 1
using .B: f as g;
g()
# 2

A.f()
# 1
B.f()
# 2

