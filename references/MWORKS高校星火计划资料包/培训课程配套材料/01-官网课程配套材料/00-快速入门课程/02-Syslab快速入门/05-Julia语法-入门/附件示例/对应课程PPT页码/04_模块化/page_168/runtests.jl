using Test
using MyProject
# 定义测试用例
test_cases = [
    (1, 10), (0, 0), (-5, 5),
    (100, 200), (-100, -50), (1, 1),
    (50, 50), (-10, 0), (-50, -40),
    (999, 1000)
]
# 运行测试用例
for (first, last) in test_cases
    @test my_sum(first, last) == sum(first:last)
end



