[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Source,

    [Parameter(Mandatory = $true)]
    [string]$Target,

    [Parameter(Mandatory = $true)]
    [string]$Plan,

    [string]$PdfOutput = ""
)

$ErrorActionPreference = "Stop"

function Get-FormulaLabel {
    param($Table)

    if ($Table.Rows.Count -ne 1 -or $Table.Columns.Count -ne 2) {
        return $null
    }

    $hasMathType = $false
    foreach ($shape in $Table.Range.InlineShapes) {
        try {
            if ($shape.OLEFormat.ProgID -eq "Equation.DSMT4") {
                $hasMathType = $true
                break
            }
        } catch {
            continue
        }
    }
    if (-not $hasMathType) {
        return $null
    }

    $number = ($Table.Cell(1, 2).Range.Text -replace "[\r\a]", "").Trim()
    $match = [regex]::Match($number, "\((?<label>\d+-\d+[a-z]?)\)")
    if (-not $match.Success) {
        throw "Cannot identify the source MathType formula number: $number"
    }
    return $match.Groups["label"].Value
}

function Set-FormulaNumber {
    param(
        $Table,
        [int]$Chapter,
        [int]$Sequence
    )

    $cell = $Table.Cell(1, 2)
    $content = $cell.Range.Duplicate
    $content.End = $content.End - 1
    # Fields in copied OLE-table cells can be dropped by a subsequent Word save.
    # The plan supplies deterministic chapter/sequence values for each equation.
    $content.Text = "($Chapter-$Sequence)"
}

function Find-MarkerParagraph {
    param(
        $Document,
        [string]$Marker
    )

    $search = $Document.Content.Duplicate
    $find = $search.Find
    $find.ClearFormatting()
    $find.Replacement.ClearFormatting()
    $find.Text = $Marker
    $find.Forward = $true
    $find.Wrap = 0
    $find.Format = $false
    $find.MatchCase = $true
    $find.MatchWholeWord = $false
    $find.MatchWildcards = $false
    if (-not $find.Execute()) {
        throw "Formula marker was not found: $Marker"
    }

    $paragraph = $search.Paragraphs.Item(1).Range.Duplicate
    $visible = ($paragraph.Text -replace "[\r\a]", "").Trim()
    if ($visible -ne $Marker) {
        throw "Formula marker must occupy its own paragraph: $Marker"
    }
    return $paragraph
}

$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$targetPath = (Resolve-Path -LiteralPath $Target).Path
$planPath = (Resolve-Path -LiteralPath $Plan).Path
$placements = @((Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json).formulas)
if ($placements.Count -eq 0) {
    throw "Formula plan is empty."
}

$word = $null
$sourceDocument = $null
$targetDocument = $null
$restorePictureSetting = $false
$originalPictureSetting = $false
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.ScreenUpdating = $false
    try {
        $originalPictureSetting = $word.Options.DoNotCompressPicturesInFile
        $word.Options.DoNotCompressPicturesInFile = $true
        $restorePictureSetting = $true
    } catch {}

    $sourceDocument = $word.Documents.Open($sourcePath, $false, $true, $false)
    $targetDocument = $word.Documents.Open($targetPath, $false, $false, $false)

    $sourceTables = @{}
    foreach ($table in $sourceDocument.Tables) {
        $label = Get-FormulaLabel $table
        if ($null -eq $label) {
            continue
        }
        if ($sourceTables.ContainsKey($label)) {
            throw "Duplicate source MathType formula label: $label"
        }
        $sourceTables[$label] = $table
    }

    if ($sourceTables.Count -ne 114) {
        throw "Source MathType formula count is $($sourceTables.Count), expected 114."
    }

    $seenSourceLabels = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($placement in $placements) {
        $sourceLabel = [string]$placement.source_label
        $marker = [string]$placement.marker
        $chapter = [int]$placement.target_chapter
        $sequence = [int]$placement.target_sequence
        if (-not $seenSourceLabels.Add($sourceLabel)) {
            throw "Formula plan duplicates source label: $sourceLabel"
        }
        if (-not $sourceTables.ContainsKey($sourceLabel)) {
            throw "Formula plan references absent source label: $sourceLabel"
        }

        $markerParagraph = Find-MarkerParagraph $targetDocument $marker
        $start = $markerParagraph.Start
        $markerParagraph.FormattedText = $sourceTables[$sourceLabel].Range.FormattedText

        $copiedTable = $null
        foreach ($candidate in $targetDocument.Tables) {
            if ($candidate.Range.Start -eq $start) {
                $copiedTable = $candidate
                break
            }
        }
        if ($null -eq $copiedTable) {
            throw "Could not locate copied MathType table for $sourceLabel."
        }
        Set-FormulaNumber $copiedTable $chapter $sequence
    }

    # Remove only the marker paragraphs after all table insertions. Deleting a
    # marker while copying changes Word's insertion behavior for later tables.
    foreach ($placement in $placements) {
        $leakedMarkerParagraph = Find-MarkerParagraph $targetDocument ([string]$placement.marker)
        $leakedMarkerParagraph.Delete()
    }

    $targetDocument.Fields.Update() | Out-Null
    foreach ($section in $targetDocument.Sections) {
        foreach ($collection in @($section.Headers, $section.Footers)) {
            foreach ($index in 1, 2, 3) {
                try {
                    $collection.Item($index).Range.Fields.Update() | Out-Null
                } catch {}
            }
        }
    }
    $targetDocument.Repaginate()
    $pages = [int]$targetDocument.ComputeStatistics(2)
    $fields = [int]$targetDocument.Fields.Count
    $targetDocument.Save()
    if ($PdfOutput) {
        $targetDocument.ExportAsFixedFormat((Resolve-Path -LiteralPath (Split-Path -Parent $PdfOutput)).Path + "\" + (Split-Path -Leaf $PdfOutput), 17, $false)
    }

    [pscustomobject]@{
        copied_formula_count = $placements.Count
        source_formula_count = $sourceTables.Count
        word_pages = $pages
        word_body_fields = $fields
    } | ConvertTo-Json -Compress
} finally {
    if ($null -ne $targetDocument) {
        try { $targetDocument.Close($false) } catch {}
    }
    if ($null -ne $sourceDocument) {
        try { $sourceDocument.Close($false) } catch {}
    }
    if ($null -ne $word) {
        if ($restorePictureSetting) {
            try { $word.Options.DoNotCompressPicturesInFile = $originalPictureSetting } catch {}
        }
        try { $word.Quit() } catch {}
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
}
