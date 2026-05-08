add_num(x, y) = x + y
# 使用 SyslabCC 时导出定义函数
@static if @isdefined(SyslabCC)
    # 生成动态库, 导出 C 函数 add_num_i64 让 C++ 调用
    # 其中，(Int, Int) 代表函数输入参数类型
    SyslabCC.static_compile(
        "add_num_i64", add_num, (Int64, Int64))
    # C 函数名可以自定义，此处使用 add_num_f64，表示双精度浮点数加法
    SyslabCC.static_compile(
        "add_num_f64", add_num, (Float64, Float64))
end

