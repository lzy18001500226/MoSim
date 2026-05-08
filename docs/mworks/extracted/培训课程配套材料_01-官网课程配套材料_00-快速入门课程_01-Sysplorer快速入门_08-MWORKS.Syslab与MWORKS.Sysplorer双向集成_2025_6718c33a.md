# 示例3-1.jl

- Source: `培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/08-MWORKS.Syslab与MWORKS.Sysplorer双向集成(2025b)/配套示例/3-FromWorkspace/示例3-1.jl`
- Category: `sysplorer_modeling`
- Score: `120`
- Size: `0.00 MB`
- Extract mode: `text`

## Extracted Text

```text
# Julia代码
table = [0 1 0 0 
         1 1 0 0 
         2 0 2 0 
         3 0 2 0]
combiTimeTableX = table[:,[1,2]] #取1,2两列
combiTimeTableY = table[:,[1,3]] #取1,3两列
combiTimeTableZ = table[:,[1,4]] #取1,4两列
```
