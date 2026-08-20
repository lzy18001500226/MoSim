[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Source,

    [Parameter(Mandatory = $true)]
    [string]$Backup,

    [string]$PdfOutput = ""
)

$ErrorActionPreference = "Stop"

function Set-ParagraphLayout {
    param(
        $Paragraph,
        [double]$Size = 10.5,
        [bool]$Bold = $false,
        [double]$Before = 0,
        [double]$After = 0,
        [double]$LineSpacing = 13
    )

    $range = $Paragraph.Range
    $range.Font.Name = "宋体"
    $range.Font.NameFarEast = "宋体"
    $range.Font.Size = $Size
    $range.Font.Bold = $Bold
    $format = $Paragraph.Format
    $format.Alignment = 0
    $format.LeftIndent = 0
    $format.RightIndent = 0
    $format.FirstLineIndent = 0
    $format.SpaceBefore = $Before
    $format.SpaceAfter = $After
    $format.LineSpacingRule = 4
    $format.LineSpacing = $LineSpacing
    $format.KeepTogether = 0
    $format.KeepWithNext = 0
}

function Replace-CellContent {
    param(
        $Cell,
        [array]$Lines,
        [double]$DefaultSize = 10.5,
        [double]$DefaultLineSpacing = 13
    )

    $content = $Cell.Range.Duplicate
    $content.End = $content.End - 1
    $content.Text = (($Lines | ForEach-Object { [string]$_.Text }) -join [char]13)

    $index = 0
    foreach ($paragraph in $Cell.Range.Paragraphs) {
        $line = if ($index -lt $Lines.Count) { $Lines[$index] } else { @{ Text = "" } }
        $size = if ($null -ne $line.Size) { [double]$line.Size } else { $DefaultSize }
        $bold = if ($null -ne $line.Bold) { [bool]$line.Bold } else { $false }
        $before = if ($null -ne $line.Before) { [double]$line.Before } else { 0 }
        $after = if ($null -ne $line.After) { [double]$line.After } else { 0 }
        $spacing = if ($null -ne $line.LineSpacing) { [double]$line.LineSpacing } else { $DefaultLineSpacing }
        Set-ParagraphLayout $paragraph $size $bold $before $after $spacing
        $index++
    }
    $Cell.VerticalAlignment = 1
}

function Set-TaskBook {
    param($Document, [int]$TableNumber)

    $table = $Document.Tables.Item($TableNumber)
    $objective = @(
        @{ Text = "课程目标："; Size = 11; Bold = $true; After = 0; LineSpacing = 13 },
        @{ Text = "通过小组项目实践，训练需求分析、系统设计、实现测试与报告表达能力，形成规范协作和结果复核意识。"; Size = 9.5; Bold = $false; After = 0; LineSpacing = 12 }
    )
    Replace-CellContent $table.Cell(4, 1) $objective 9.5 12

    $taskCell = $table.Cell(5, 1)
    $nested = $taskCell.Tables.Item(1)
    if ($nested.Rows.Item(1).Cells.Count -eq 3) {
        $nested.Cell(1, 1).Merge($nested.Cell(1, 3))
    }

    $description = @(
        @{ Text = "课题任务与场景："; Size = 10; Bold = $true; After = 1; LineSpacing = 12 },
        @{ Text = "课题名称：基于 MWORKS 的四旋翼位姿控制平台。"; Size = 9.5; Bold = $false; After = 0; LineSpacing = 11.5 },
        @{ Text = "场景及意义：面向四旋翼控制教学与工程验证，建立云纵150参照模型、统一控制器接口和可追溯实验链路。"; Size = 9.5; Bold = $false; After = 0; LineSpacing = 11.5 },
        @{ Text = "具体要求：完成公共 Plant 和参数说明；统一控制器与任务配置并保留可复现记录；完成 MWORKS 检查、仿真、测试及代表性 Sysblock/C99/SIL 交付；区分静态、仿真、ROS1/PX4/Gazebo 运行时与显示证据。"; Size = 9.5; Bold = $false; After = 0; LineSpacing = 11.5 },
        @{ Text = "进程安排："; Size = 9.5; Bold = $true; Before = 1; After = 0; LineSpacing = 11.5 }
    )
    Replace-CellContent $nested.Cell(1, 1) $description 9.5 11.5

    $schedule = @(
        @(@{ Text = "序号"; Size = 9.5; Bold = $true }, @{ Text = "内容"; Size = 9.5; Bold = $true }, @{ Text = "天数"; Size = 9.5; Bold = $true }),
        @(@{ Text = "1"; Size = 9.5 }, @{ Text = "选题与需求分析"; Size = 9.5 }, @{ Text = "7"; Size = 9.5 }),
        @(@{ Text = "2"; Size = 9.5 }, @{ Text = "系统设计与编码实现"; Size = 9.5 }, @{ Text = "5"; Size = 9.5 }),
        @(@{ Text = "3"; Size = 9.5 }, @{ Text = "测试评估与验收"; Size = 9.5 }, @{ Text = "1"; Size = 9.5 }),
        @(@{ Text = "4"; Size = 9.5 }, @{ Text = "整理课程实践报告"; Size = 9.5 }, @{ Text = "1"; Size = 9.5 })
    )
    for ($row = 2; $row -le 6; $row++) {
        for ($column = 1; $column -le 3; $column++) {
            Replace-CellContent $nested.Cell($row, $column) @($schedule[$row - 2][$column - 1]) 9.5 11.5
        }
        $nested.Rows.Item($row).HeightRule = 2
        $nested.Rows.Item($row).Height = 20
        $nested.Rows.Item($row).AllowBreakAcrossPages = 0
    }
    $nested.Rows.Item(1).HeightRule = 0
    $nested.Rows.Item(1).Height = 0
    $nested.Rows.Item(1).AllowBreakAcrossPages = 0
    $nested.AllowAutoFit = $false

    $table.Rows.Item(4).HeightRule = 0
    $table.Rows.Item(4).Height = 0
    $table.Rows.Item(5).HeightRule = 0
    $table.Rows.Item(5).Height = 0
    $table.Rows.Item(4).AllowBreakAcrossPages = 0
    $table.Rows.Item(5).AllowBreakAcrossPages = 0
}

function Set-DefenseRecord {
    param(
        $Document,
        [int]$TableNumber,
        [string]$Name,
        [array]$Questions
    )

    $table = $Document.Tables.Item($TableNumber)
    $cell = $table.Cell(3, 1)
    $lines = @(@{ Text = "答辩记录："; Size = 11.5; Bold = $true; Before = 0; After = 4; LineSpacing = 14 })
    foreach ($item in $Questions) {
        $lines += @{ Text = "问题：$($item.Question)"; Size = 10.5; Bold = $true; Before = 3; After = 1; LineSpacing = 13.5 }
        $lines += @{ Text = "回答：$($item.Answer)"; Size = 10.5; Bold = $false; Before = 0; After = 2; LineSpacing = 13.5 }
    }
    $lines += @{ Text = "答辩人：$Name　　　　　　　　　　　　　　　　日期：2026.07.18"; Size = 10; Bold = $false; Before = 4; After = 0; LineSpacing = 13 }
    Replace-CellContent $cell $lines 10.5 13.5
    $table.Rows.Item(3).HeightRule = 0
    $table.Rows.Item(3).Height = 0
    $table.Rows.Item(3).AllowBreakAcrossPages = 0
}

$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$backupPath = (Resolve-Path -LiteralPath (Split-Path -Parent $Backup)).Path + "\" + (Split-Path -Leaf $Backup)
Copy-Item -LiteralPath $sourcePath -Destination $backupPath -Force

$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.ScreenUpdating = $false
    $document = $word.Documents.Open($sourcePath, $false, $false, $false)

    foreach ($tableNumber in 6..10) {
        Write-Output ("task_table=" + $tableNumber)
        Set-TaskBook $document $tableNumber
    }

    Write-Output "defense_tables=11-15"
    Set-DefenseRecord $document 11 "刘致远" @(
        @{ Question = "如果只保留一张仿真截图，为什么不能证明项目结论成立？"; Answer = "截图看不出模型、控制器、任务配置和结果是否属于同一次运行，也无法复核指标来源。至少应绑定模型路径、控制器路由、任务 Profile、原始结果、指标和运行清单。" },
        @{ Question = "CheckModel 通过但结果时间序列为空时，能否写成仿真成功？"; Answer = "不能。CheckModel 只说明结构可检查；还要有非空时间序列、有效参考值、有限指标和同次运行记录。缺少这些条件应标为阻塞或无效。" },
        @{ Question = "MWORKS、ROS1/PX4/Gazebo 和界面截图分别回答什么问题？"; Answer = "MWORKS 支撑模型与正式仿真结果；ROS1/PX4/Gazebo 支撑独立运行时的生命周期和日志事实；Studio、QGC、RViz、UE 主要支撑配置、操作或显示状态，不能互相替代。" }
    )
    Set-DefenseRecord $document 12 "钟俊杰" @(
        @{ Question = "虚拟机体参数来自资料而非实测时，报告应怎样表述？"; Answer = "应写明参数单位、来源和适用范围；没有实测依据的惯量、气动和电机动态只能作为工程参数或待校准项，不能表述为真实飞行辨识结果。" },
        @{ Question = "如何在分析控制器之前排查坐标系和单位错误？"; Answer = "先固定世界系、机体系、角度单位、推力单位和采样语义，再用静态接口检查和隔离输入核对位置、速度、姿态及旋翼映射，确认映射正确后再看闭环指标。" },
        @{ Question = "公共 Plant 的电机动态和故障参数需要留下哪些证据？"; Answer = "应保留参数 Profile、源文件、注入配置和同次运行日志，并区分模型中声明的故障效果与真实系统容错性能；后者不能由虚拟机体仿真单独推出。" }
    )
    Set-DefenseRecord $document 13 "朱尚吉" @(
        @{ Question = "为什么要把控制器输出划分为统一边界，而不是让每条路线直接连接 Plant？"; Answer = "统一边界固定输入输出的维度、单位和语义，Adapter 负责转换与边界检查，公共 Plant 和指标保持不变，新增或替换控制器时更容易定位差异。" },
        @{ Question = "Adapter、FormalRunner 和 Plant 的职责怎样分开？"; Answer = "Adapter 只转换控制律输出并执行边界检查；FormalRunner 固定任务、求解器、采样和结果读取；Plant 描述机体、执行器和传感器。分层后，替换控制器不会暗中改变实验条件。" },
        @{ Question = "怎样判断两条控制器路线的对比是公平的？"; Answer = "两条路线应使用同一 Plant、任务、初值、采样、求解器和指标，并且各自形成有效结果；只有路由登记、窗口打开或单张曲线都不能算完成公平对比。" }
    )
    Set-DefenseRecord $document 14 "陈健" @(
        @{ Question = "从 Sysblock 到可运行 C99，中间哪些交付物必须留痕？"; Answer = "应保存 Sysblock 源模型、生成 C99、稳定 C ABI 包装、构建日志、固定向量结果及源文件和生成物哈希，确保运行代码能回到具体模型和配置。" },
        @{ Question = "固定向量测试能证明什么，不能证明什么？"; Answer = "它能验证接口顺序、维度、单位映射和部分边界行为，但不能替代整机 SIL、MWORKS 正式仿真、ROS1 运行时或真实飞行验收。" },
        @{ Question = "C99 构建通过但 SIL 结果不一致时，应按什么顺序排查？"; Answer = "先比对输入输出顺序、单位、坐标帧、采样保持和初始化，再核对源文件与生成物哈希；差异未解释前，不能把构建通过写成控制器通过。" }
    )
    Set-DefenseRecord $document 15 "王家祺" @(
        @{ Question = "运行时日志、MWORKS 结果和界面截图分别能证明什么？"; Answer = "MWORKS 结果回答仿真变量和指标；ROS1/PX4/Gazebo 日志回答任务生命周期、注入动作和运行时事实；Studio、QGC、RViz、UE 截图只回答界面或显示状态。" },
        @{ Question = "遇到超时、空变量或未知状态时，报告应如何处理？"; Answer = "保留原始日志和部分结果，明确标为失败、阻塞、无效或待验证，并写清触发条件和缺失证据；不能用截图、窗口出现或最后一帧画面替代成功。" },
        @{ Question = "怎样让别人从一张报告图表复核到原始事实？"; Answer = "图表应能回链到配置、参数来源、源码版本或哈希、运行环境、原始结果、指标、日志和图表生成脚本，结论只使用这些材料实际支持的范围。" }
    )

    $document.Repaginate()
    $document.Fields.Update() | Out-Null
    foreach ($section in $document.Sections) {
        foreach ($collection in @($section.Headers, $section.Footers)) {
            foreach ($index in 1, 2, 3) {
                try { $collection.Item($index).Range.Fields.Update() | Out-Null } catch {}
            }
        }
    }
    $document.Save()
    $pages = [int]$document.ComputeStatistics(2)
    if ($PdfOutput) {
        $pdfPath = (Resolve-Path -LiteralPath (Split-Path -Parent $PdfOutput)).Path + "\" + (Split-Path -Leaf $PdfOutput)
        $document.ExportAsFixedFormat($pdfPath, 17, $false)
    }
    [pscustomobject]@{
        output = $sourcePath
        backup = $backupPath
        pages = $pages
        task_tables = 5
        defense_tables = 5
        pdf = $PdfOutput
    } | ConvertTo-Json -Compress
} finally {
    if ($null -ne $document) { try { $document.Close($false) } catch {} }
    if ($null -ne $word) { try { $word.Quit() } catch {} }
}
