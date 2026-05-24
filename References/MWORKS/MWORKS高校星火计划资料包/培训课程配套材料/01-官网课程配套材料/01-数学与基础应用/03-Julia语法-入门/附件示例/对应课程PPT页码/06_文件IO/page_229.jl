using CSV
using DataFrames
# 设置 delim='\t' 来指定制表符作为字段分隔符
data = DataFrame(Name=["Alice", "Bob", "Charlie"], Age=[25, 30, 35], Salary=[50000, 60000, 70000])
# 导出 DataFrame 到 TSV 文件
CSV.write("output.tsv", data, delim='\t')
# 读取文件内容
data = CSV.read("output.tsv", DataFrame, delim='\t')
println(first(data, 2))



