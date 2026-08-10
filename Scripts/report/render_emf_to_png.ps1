[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath,
    [double]$Scale = 1.0
)

$resolvedInput = [IO.Path]::GetFullPath($InputPath)
$resolvedOutput = [IO.Path]::GetFullPath($OutputPath)
if (-not (Test-Path -LiteralPath $resolvedInput -PathType Leaf)) {
    throw "EMF input does not exist: $resolvedInput"
}
if (Test-Path -LiteralPath $resolvedOutput) {
    throw "Refusing to overwrite PNG output: $resolvedOutput"
}
if ($Scale -le 0) {
    throw "Scale must be positive"
}

Add-Type -AssemblyName System.Drawing
$outputDirectory = Split-Path -Parent $resolvedOutput
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
$bytes = [IO.File]::ReadAllBytes($resolvedInput)
$stream = [IO.MemoryStream]::new($bytes)
$metafile = [Drawing.Imaging.Metafile]::new($stream)
$bitmap = $null
$graphics = $null
try {
    $width = [Math]::Max(32, [int][Math]::Round($metafile.Width * $Scale))
    $height = [Math]::Max(32, [int][Math]::Round($metafile.Height * $Scale))
    $bitmap = [Drawing.Bitmap]::new(
        $width,
        $height,
        [Drawing.Imaging.PixelFormat]::Format32bppArgb
    )
    $graphics = [Drawing.Graphics]::FromImage($bitmap)
    $graphics.Clear([Drawing.Color]::White)
    $graphics.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::HighQuality
    $graphics.DrawImage($metafile, 0, 0, $width, $height)
    $bitmap.Save($resolvedOutput, [Drawing.Imaging.ImageFormat]::Png)
}
finally {
    if ($null -ne $graphics) { $graphics.Dispose() }
    if ($null -ne $bitmap) { $bitmap.Dispose() }
    $metafile.Dispose()
    $stream.Dispose()
}

Get-Item -LiteralPath $resolvedOutput | Select-Object FullName, Length
