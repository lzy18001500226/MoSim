param(
    [string]$OutputDirectory = (Join-Path $PSScriptRoot '..\图\项目图件\设计图')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$script:TitleFont = [System.Drawing.Font]::new('Microsoft YaHei', 30, [System.Drawing.FontStyle]::Bold)
$script:HeadingFont = [System.Drawing.Font]::new('Microsoft YaHei', 23, [System.Drawing.FontStyle]::Bold)
$script:BodyFont = [System.Drawing.Font]::new('Microsoft YaHei', 19, [System.Drawing.FontStyle]::Regular)
$script:SmallFont = [System.Drawing.Font]::new('Microsoft YaHei', 16, [System.Drawing.FontStyle]::Regular)
$script:TextBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(31, 41, 55))
$script:MutedBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(75, 85, 99))
$script:BorderColor = [System.Drawing.Color]::FromArgb(71, 85, 105)

function New-Canvas {
    param([int]$Width, [int]$Height)

    $bitmap = [System.Drawing.Bitmap]::new($Width, $Height)
    $bitmap.SetResolution(150, 150)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $graphics.Clear([System.Drawing.Color]::White)
    return [pscustomobject]@{ Bitmap = $bitmap; Graphics = $graphics }
}

function Save-Canvas {
    param($Canvas, [string]$Path)

    $directory = Split-Path -Parent $Path
    $temporaryPath = Join-Path $directory ('.' + [System.IO.Path]::GetFileName($Path) + '.' + [System.Guid]::NewGuid().ToString('N') + '.tmp')
    $backupPath = Join-Path $directory ('.' + [System.IO.Path]::GetFileName($Path) + '.' + [System.Guid]::NewGuid().ToString('N') + '.bak')
    try {
        $Canvas.Bitmap.Save($temporaryPath, [System.Drawing.Imaging.ImageFormat]::Png)
        if (Test-Path -LiteralPath $Path) {
            [System.IO.File]::Replace($temporaryPath, $Path, $backupPath)
        }
        else {
            [System.IO.File]::Move($temporaryPath, $Path)
        }
    }
    finally {
        $Canvas.Graphics.Dispose()
        $Canvas.Bitmap.Dispose()
        if (Test-Path -LiteralPath $temporaryPath) {
            Remove-Item -LiteralPath $temporaryPath -Force
        }
        if (Test-Path -LiteralPath $backupPath) {
            Remove-Item -LiteralPath $backupPath -Force
        }
    }
}

function Draw-Title {
    param([System.Drawing.Graphics]$Graphics, [string]$Text, [int]$Width)

    $format = [System.Drawing.StringFormat]::new()
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $rect = [System.Drawing.RectangleF]::new(0, 26, $Width, 55)
    $Graphics.DrawString($Text, $script:TitleFont, $script:TextBrush, $rect, $format)
    $format.Dispose()
}

function Draw-CenteredText {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Text,
        [System.Drawing.Font]$Font,
        [System.Drawing.Brush]$Brush,
        [int]$X,
        [int]$Y,
        [int]$Width,
        [int]$Height
    )

    $format = [System.Drawing.StringFormat]::new()
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $format.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit
    $rect = [System.Drawing.RectangleF]::new($X, $Y, $Width, $Height)
    $Graphics.DrawString($Text, $Font, $Brush, $rect, $format)
    $format.Dispose()
}

function Draw-Box {
    param(
        [System.Drawing.Graphics]$Graphics,
        [int]$X,
        [int]$Y,
        [int]$Width,
        [int]$Height,
        [System.Drawing.Color]$Fill,
        [string]$Text,
        [System.Drawing.Font]$Font = $script:BodyFont
    )

    $fillBrush = [System.Drawing.SolidBrush]::new($Fill)
    $pen = [System.Drawing.Pen]::new($script:BorderColor, 2.5)
    $rect = [System.Drawing.Rectangle]::new($X, $Y, $Width, $Height)
    $Graphics.FillRectangle($fillBrush, $rect)
    $Graphics.DrawRectangle($pen, $rect)
    Draw-CenteredText $Graphics $Text $Font $script:TextBrush $X $Y $Width $Height
    $pen.Dispose()
    $fillBrush.Dispose()
}

function Draw-RoundedBox {
    param(
        [System.Drawing.Graphics]$Graphics,
        [int]$X,
        [int]$Y,
        [int]$Width,
        [int]$Height,
        [System.Drawing.Color]$Fill,
        [string]$Text,
        [System.Drawing.Font]$Font = $script:BodyFont
    )

    $radius = 22
    $path = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $path.AddArc($X, $Y, $radius, $radius, 180, 90)
    $path.AddArc($X + $Width - $radius, $Y, $radius, $radius, 270, 90)
    $path.AddArc($X + $Width - $radius, $Y + $Height - $radius, $radius, $radius, 0, 90)
    $path.AddArc($X, $Y + $Height - $radius, $radius, $radius, 90, 90)
    $path.CloseFigure()
    $fillBrush = [System.Drawing.SolidBrush]::new($Fill)
    $pen = [System.Drawing.Pen]::new($script:BorderColor, 2.5)
    $Graphics.FillPath($fillBrush, $path)
    $Graphics.DrawPath($pen, $path)
    Draw-CenteredText $Graphics $Text $Font $script:TextBrush $X $Y $Width $Height
    $pen.Dispose()
    $fillBrush.Dispose()
    $path.Dispose()
}

function Draw-UseCase {
    param(
        [System.Drawing.Graphics]$Graphics,
        [int]$X,
        [int]$Y,
        [int]$Width,
        [int]$Height,
        [string]$Text
    )

    $fillBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(239, 246, 255))
    $pen = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(37, 99, 235), 2.5)
    $Graphics.FillEllipse($fillBrush, $X, $Y, $Width, $Height)
    $Graphics.DrawEllipse($pen, $X, $Y, $Width, $Height)
    Draw-CenteredText $Graphics $Text $script:BodyFont $script:TextBrush $X $Y $Width $Height
    $pen.Dispose()
    $fillBrush.Dispose()
}

function Draw-Actor {
    param([System.Drawing.Graphics]$Graphics, [int]$CenterX, [int]$TopY, [string]$Label)

    $pen = [System.Drawing.Pen]::new($script:BorderColor, 3)
    $Graphics.DrawEllipse($pen, $CenterX - 18, $TopY, 36, 36)
    $Graphics.DrawLine($pen, $CenterX, $TopY + 36, $CenterX, $TopY + 100)
    $Graphics.DrawLine($pen, $CenterX - 34, $TopY + 60, $CenterX + 34, $TopY + 60)
    $Graphics.DrawLine($pen, $CenterX, $TopY + 100, $CenterX - 30, $TopY + 140)
    $Graphics.DrawLine($pen, $CenterX, $TopY + 100, $CenterX + 30, $TopY + 140)
    $labelRect = [System.Drawing.RectangleF]::new($CenterX - 135, $TopY + 154, 270, 88)
    $labelFormat = [System.Drawing.StringFormat]::new()
    $labelFormat.Alignment = [System.Drawing.StringAlignment]::Center
    $labelFormat.LineAlignment = [System.Drawing.StringAlignment]::Center
    $Graphics.DrawString($Label, $script:BodyFont, $script:TextBrush, $labelRect, $labelFormat)
    $labelFormat.Dispose()
    $pen.Dispose()
}

function Draw-Association {
    param([System.Drawing.Graphics]$Graphics, [int]$X1, [int]$Y1, [int]$X2, [int]$Y2)

    $pen = [System.Drawing.Pen]::new($script:BorderColor, 2)
    $Graphics.DrawLine($pen, $X1, $Y1, $X2, $Y2)
    $pen.Dispose()
}

function Draw-Arrow {
    param(
        [System.Drawing.Graphics]$Graphics,
        [int]$X1,
        [int]$Y1,
        [int]$X2,
        [int]$Y2,
        [System.Drawing.Color]$Color = $script:BorderColor,
        [float]$Width = 2.5
    )

    $pen = [System.Drawing.Pen]::new($Color, $Width)
    $pen.CustomEndCap = [System.Drawing.Drawing2D.AdjustableArrowCap]::new(10, 12, $true)
    $Graphics.DrawLine($pen, $X1, $Y1, $X2, $Y2)
    $pen.Dispose()
}

function Draw-Decision {
    param([System.Drawing.Graphics]$Graphics, [int]$CenterX, [int]$TopY, [int]$Size, [string]$Text)

    $points = [System.Drawing.Point[]]@(
        [System.Drawing.Point]::new($CenterX, $TopY),
        [System.Drawing.Point]::new($CenterX + $Size, $TopY + $Size),
        [System.Drawing.Point]::new($CenterX, $TopY + 2 * $Size),
        [System.Drawing.Point]::new($CenterX - $Size, $TopY + $Size)
    )
    $fillBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(254, 249, 195))
    $pen = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(202, 138, 4), 2.5)
    $Graphics.FillPolygon($fillBrush, $points)
    $Graphics.DrawPolygon($pen, $points)
    Draw-CenteredText $Graphics $Text $script:SmallFont $script:TextBrush ($CenterX - $Size + 10) ($TopY + 15) (2 * $Size - 20) (2 * $Size - 30)
    $pen.Dispose()
    $fillBrush.Dispose()
}

function Draw-Note {
    param([System.Drawing.Graphics]$Graphics, [string]$Text, [int]$X, [int]$Y, [int]$Width)

    $rect = [System.Drawing.RectangleF]::new($X, $Y, $Width, 70)
    $format = [System.Drawing.StringFormat]::new()
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $Graphics.DrawString($Text, $script:SmallFont, $script:MutedBrush, $rect, $format)
    $format.Dispose()
}

function Write-UseCaseDiagram {
    param([string]$Path)

    $canvas = New-Canvas 2200 1220
    $g = $canvas.Graphics
    Draw-Title $g 'MoSim 系统用例图' 2200

    $boundaryPen = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(30, 64, 175), 3)
    $boundaryBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(239, 246, 255))
    $g.FillRectangle($boundaryBrush, 400, 130, 1370, 920)
    $g.DrawRectangle($boundaryPen, 400, 130, 1370, 920)
    Draw-CenteredText $g 'MoSim 四旋翼仿真与控制平台' $script:HeadingFont $script:TextBrush 730 145 720 45

    Draw-Actor $g 185 435 '使用者'
    Draw-Actor $g 1990 245 '维护者'
    Draw-Actor $g 1990 565 "MWORKS`n仿真环境"
    Draw-Actor $g 1990 850 "ROS1/PX4`nGazebo"

    Draw-UseCase $g 625 275 395 105 '配置实验任务'
    Draw-UseCase $g 1125 275 470 105 '运行模型检查与仿真'
    Draw-UseCase $g 625 515 395 105 '查看指标与结果'
    Draw-UseCase $g 1125 515 470 105 '生成 C99 并完成 SIL'
    Draw-UseCase $g 840 760 525 105 '登记运行时任务与记录'

    Draw-Association $g 250 505 625 328
    Draw-Association $g 250 505 1125 328
    Draw-Association $g 250 505 625 568
    Draw-Association $g 1935 315 1595 328
    Draw-Association $g 1935 315 1595 568
    Draw-Association $g 1935 635 1595 328
    Draw-Association $g 1935 920 1365 812

    $boundaryPen.Dispose()
    $boundaryBrush.Dispose()
    Save-Canvas $canvas $Path
}

function Write-ArchitectureDiagram {
    param([string]$Path)

    $canvas = New-Canvas 2200 1300
    $g = $canvas.Graphics
    Draw-Title $g 'MoSim 分层软件体系结构图' 2200

    $layers = @(
        @{ Y = 140; Label = '操作与辅助层'; Fill = [System.Drawing.Color]::FromArgb(240, 249, 255); Parts = @('MoSim Studio', 'QGC / RViz / UE', '只读本地助手') },
        @{ Y = 350; Label = '交付与运行层'; Fill = [System.Drawing.Color]::FromArgb(255, 247, 237); Parts = @('代码生成与 C99 ABI', 'ROS1/PX4/Gazebo 适配器', '构建与 SIL') },
        @{ Y = 560; Label = '实验执行层'; Fill = [System.Drawing.Color]::FromArgb(240, 253, 244); Parts = @('任务 Profile', 'FormalRunner', '原始结果与指标') },
        @{ Y = 770; Label = '控制器接口层'; Fill = [System.Drawing.Color]::FromArgb(254, 252, 232); Parts = @('控制器实现', 'Adapter 与输出合同', '控制分配') },
        @{ Y = 980; Label = '物理模型层'; Fill = [System.Drawing.Color]::FromArgb(250, 245, 255); Parts = @('Modelica 公共 Plant', '旋翼执行器', '参数 Profile') }
    )

    foreach ($layer in $layers) {
        Draw-Box $g 170 $layer.Y 300 125 $layer.Fill $layer.Label $script:HeadingFont
        $x = 530
        foreach ($part in $layer.Parts) {
            Draw-RoundedBox $g $x ($layer.Y + 15) 430 95 ([System.Drawing.Color]::White) $part $script:BodyFont
            $x += 500
        }
    }

    foreach ($centerX in @(745, 1245, 1745)) {
        Draw-Arrow $g $centerX 265 $centerX 350 ([System.Drawing.Color]::FromArgb(59, 130, 246))
        Draw-Arrow $g $centerX 475 $centerX 560 ([System.Drawing.Color]::FromArgb(59, 130, 246))
        Draw-Arrow $g $centerX 685 $centerX 770 ([System.Drawing.Color]::FromArgb(59, 130, 246))
        Draw-Arrow $g $centerX 895 $centerX 980 ([System.Drawing.Color]::FromArgb(59, 130, 246))
    }

    Draw-Note $g '各层通过配置、接口合同和结果文件连接；MWORKS 模型、运行时记录和显示界面分别承担不同职责。' 325 1165 1550
    Save-Canvas $canvas $Path
}

function Write-ActivityDiagram {
    param([string]$Path)

    $canvas = New-Canvas 2100 1360
    $g = $canvas.Graphics
    Draw-Title $g '正式实验核心活动图' 2100

    $center = 1050
    $blackBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(31, 41, 55))
    $g.FillEllipse($blackBrush, $center - 16, 115, 32, 32)
    Draw-RoundedBox $g 835 190 430 75 ([System.Drawing.Color]::FromArgb(239, 246, 255)) '配置任务与控制器'
    Draw-RoundedBox $g 835 320 430 75 ([System.Drawing.Color]::FromArgb(239, 246, 255)) '校验任务配置'
    Draw-Decision $g $center 450 65 '配置有效？'
    Draw-RoundedBox $g 835 650 430 75 ([System.Drawing.Color]::FromArgb(240, 253, 244)) '执行 CheckModel'
    Draw-Decision $g $center 780 65 '检查通过？'
    Draw-RoundedBox $g 835 980 430 75 ([System.Drawing.Color]::FromArgb(240, 253, 244)) '启动正式仿真'
    Draw-Decision $g $center 1110 65 '结果有效？'

    Draw-RoundedBox $g 100 540 460 75 ([System.Drawing.Color]::FromArgb(255, 247, 237)) '配置无效，修改任务'
    Draw-RoundedBox $g 100 870 460 75 ([System.Drawing.Color]::FromArgb(254, 242, 242)) '检查未通过，记录失败'
    Draw-RoundedBox $g 1460 1180 460 75 ([System.Drawing.Color]::FromArgb(254, 242, 242)) '结果无效，记录中断'
    Draw-RoundedBox $g 835 1245 430 75 ([System.Drawing.Color]::FromArgb(240, 253, 244)) '归档结果并计算指标'

    Draw-Arrow $g $center 147 $center 190
    Draw-Arrow $g $center 265 $center 320
    Draw-Arrow $g $center 395 $center 450
    Draw-Arrow $g $center 580 $center 650
    Draw-Arrow $g $center 725 $center 780
    Draw-Arrow $g $center 910 $center 980
    Draw-Arrow $g $center 1055 $center 1110
    Draw-Arrow $g $center 1240 $center 1245

    Draw-Arrow $g 985 515 560 575 ([System.Drawing.Color]::FromArgb(217, 119, 6))
    Draw-Arrow $g 560 615 835 358 ([System.Drawing.Color]::FromArgb(217, 119, 6))
    Draw-Arrow $g 985 845 560 908 ([System.Drawing.Color]::FromArgb(220, 38, 38))
    Draw-Arrow $g 1115 1175 1460 1218 ([System.Drawing.Color]::FromArgb(220, 38, 38))
    $g.FillEllipse($blackBrush, $center - 16, 1325, 32, 32)
    $blackBrush.Dispose()
    Save-Canvas $canvas $Path
}

function Write-DataFlowDiagram {
    param([string]$Path)

    $canvas = New-Canvas 2200 1100
    $g = $canvas.Graphics
    Draw-Title $g '配置到报告的数据流图' 2200

    Draw-Box $g 95 300 330 170 ([System.Drawing.Color]::FromArgb(239, 246, 255)) "机体 Profile`n路由合同`n实验 Profile" $script:BodyFont
    Draw-Box $g 535 300 330 170 ([System.Drawing.Color]::FromArgb(254, 252, 232)) "任务配置`nJSON / Modelica harness" $script:BodyFont
    Draw-Box $g 975 270 390 230 ([System.Drawing.Color]::FromArgb(240, 253, 244)) "MWORKS / Modelica`nFormalRunner`n或运行时后端" $script:BodyFont
    Draw-Box $g 1475 300 300 170 ([System.Drawing.Color]::FromArgb(255, 247, 237)) "原始结果`nResult.msr / CSV`n运行日志" $script:BodyFont
    Draw-Box $g 1820 300 320 170 ([System.Drawing.Color]::FromArgb(250, 245, 255)) "指标与报告`nMETRICS.json`n图表与正文" $script:SmallFont

    Draw-Box $g 1115 690 520 145 ([System.Drawing.Color]::FromArgb(254, 242, 242)) "运行清单`nRUN_MANIFEST.json`n后端与生命周期状态" $script:SmallFont

    Draw-Arrow $g 425 385 535 385 ([System.Drawing.Color]::FromArgb(37, 99, 235))
    Draw-Arrow $g 865 385 975 385 ([System.Drawing.Color]::FromArgb(37, 99, 235))
    Draw-Arrow $g 1365 385 1475 385 ([System.Drawing.Color]::FromArgb(37, 99, 235))
    Draw-Arrow $g 1775 385 1820 385 ([System.Drawing.Color]::FromArgb(37, 99, 235))
    Draw-Arrow $g 1365 500 1375 690 ([System.Drawing.Color]::FromArgb(220, 38, 38))
    Draw-Arrow $g 1635 760 1820 445 ([System.Drawing.Color]::FromArgb(220, 38, 38))

    Draw-CenteredText $g '参数与任务选择' $script:SmallFont $script:MutedBrush 410 500 150 35
    Draw-CenteredText $g '执行输入' $script:SmallFont $script:MutedBrush 840 500 160 35
    Draw-CenteredText $g '原始观测' $script:SmallFont $script:MutedBrush 1340 500 160 35
    Draw-CenteredText $g '计算与归档' $script:SmallFont $script:MutedBrush 1750 500 170 35
    Draw-Note $g '报告只使用可追溯的原始结果、指标和运行清单；截图不作为数据来源。' 400 925 1400
    Save-Canvas $canvas $Path
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
Write-UseCaseDiagram (Join-Path $OutputDirectory 'use-case-diagram.png')
Write-ArchitectureDiagram (Join-Path $OutputDirectory 'software-architecture.png')
Write-ActivityDiagram (Join-Path $OutputDirectory 'formal-experiment-activity.png')
Write-DataFlowDiagram (Join-Path $OutputDirectory 'audit-dataflow.png')

$script:TitleFont.Dispose()
$script:HeadingFont.Dispose()
$script:BodyFont.Dispose()
$script:SmallFont.Dispose()
$script:TextBrush.Dispose()
$script:MutedBrush.Dispose()
