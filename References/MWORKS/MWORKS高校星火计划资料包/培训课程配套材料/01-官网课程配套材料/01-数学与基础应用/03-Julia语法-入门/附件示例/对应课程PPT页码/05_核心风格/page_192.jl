f() = rand(Bool) ? 0 : 1.0
@code_warntype f()
@btime f();
@btime sum($([f() for i in 1:1024]));


f() = rand(Bool) ? 0.0 : 1.0
@code_warntype f()
@btime f();
@btime sum($([f() for i in 1:1024]));