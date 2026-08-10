[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Source,
    [Parameter(Mandatory = $true)]
    [string]$Manifest,
    [Parameter(Mandatory = $true)]
    [string]$Output,
    [Parameter(Mandatory = $true)]
    [string]$Audit,
    [int[]]$FormulaId,
    [int]$SaveEvery = 8,
    [string]$ProgressLog,
    [switch]$Execute
)

<#+
.SYNOPSIS
    Convert native report equations to editable Equation.DSMT4 objects without
    foreground text entry.

.DESCRIPTION
    The source report is copied to a new output.  Each selected native OMML
    equation is deleted and replaced by a Word-internal FormattedText copy of
    an existing Equation.DSMT4 container.  The copied OLE object is updated
    through MathType's MathML IDataObject format.  The script never selects a
    range, activates a window, invokes the MathType TeX toggle command, or
    uses the Windows clipboard.

    Execution is opt-in.  Without -Execute this script only validates the
    manifest and prints a plan; it does not start Word or MathType.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$helperPath = Join-Path $PSScriptRoot 'MathTypeOleData.cs'

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)

    $hash = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        return ([System.BitConverter]::ToString($hash.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $stream.Dispose()
        $hash.Dispose()
    }
}

function Get-ProcessSnapshot {
    return @(
        Get-Process | Where-Object { $_.ProcessName -in @('WINWORD', 'MathType') } |
            ForEach-Object {
                [ordered]@{
                    id = $_.Id
                    name = $_.ProcessName
                    main_window_handle = [int64]$_.MainWindowHandle
                    main_window_title = [string]$_.MainWindowTitle
                }
            }
    )
}

function Resolve-ExistingPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    return (Resolve-Path -LiteralPath $Path).Path
}

function Get-ManifestRecords {
    param([Parameter(Mandatory = $true)][string]$Path)

    $manifest = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    $records = @($manifest.formulas)
    if ($records.Count -ne 104) {
        throw "MathType manifest must contain 104 formulas; found $($records.Count)."
    }

    $expectedIds = 1..104
    $actualIds = @($records | ForEach-Object { [int]$_.formula_id })
    if (-not [System.Linq.Enumerable]::SequenceEqual(
            [int[]]$expectedIds,
            [int[]]$actualIds
        )) {
        throw 'MathType manifest formula IDs must be contiguous from 1 through 104.'
    }

    foreach ($record in $records) {
        if ([string]::IsNullOrWhiteSpace([string]$record.mathml) -or
            -not ([string]$record.mathml).Trim().StartsWith('<math')) {
            throw "Formula $($record.formula_id) has no MathML document element."
        }
    }
    return $records
}

function Select-FormulaRecords {
    param(
        [Parameter(Mandatory = $true)]$Records,
        [int[]]$RequestedIds
    )

    if ($null -eq $RequestedIds -or $RequestedIds.Count -eq 0) {
        return @($Records)
    }

    $uniqueIds = @($RequestedIds | Sort-Object -Unique)
    if ($uniqueIds.Count -ne $RequestedIds.Count) {
        throw 'FormulaId values must be unique.'
    }
    foreach ($id in $uniqueIds) {
        if ($id -lt 1 -or $id -gt 104) {
            throw "FormulaId $id is outside the supported range 1..104."
        }
    }
    return @(
        $Records |
            Where-Object { [int]$_.formula_id -in $uniqueIds } |
            Sort-Object { [int]$_.formula_id }
    )
}

function Get-MathTypeShapes {
    param([Parameter(Mandatory = $true)]$Document)

    $shapes = @()
    for ($index = 1; $index -le $Document.InlineShapes.Count; $index++) {
        $shape = $Document.InlineShapes.Item($index)
        try {
            if ([string]$shape.OLEFormat.ProgID -eq 'Equation.DSMT4') {
                $shapes += $shape
            }
        }
        catch {
            # Non-OLE inline shapes do not expose OLEFormat.
        }
    }
    return ,$shapes
}

function Get-MathTypeInventory {
    param([Parameter(Mandatory = $true)]$Document)

    $shapes = @()
    $byNumber = @{}
    for ($index = 1; $index -le $Document.InlineShapes.Count; $index++) {
        $shape = $Document.InlineShapes.Item($index)
        try {
            if ([string]$shape.OLEFormat.ProgID -ne 'Equation.DSMT4') {
                continue
            }
            $shapes += $shape
            if ($shape.Range.Tables.Count -ne 1) {
                continue
            }
            $tableText = [string]$shape.Range.Tables.Item(1).Range.Text
            $matches = [regex]::Matches($tableText, '\((\d+-\d+[a-z]?)\)')
            if ($matches.Count -eq 0) {
                continue
            }
            $number = $matches[$matches.Count - 1].Groups[1].Value
            if ($byNumber.ContainsKey($number)) {
                throw "Duplicate Equation.DSMT4 table number detected: ($number)."
            }
            $byNumber[$number] = $shape
        }
        catch {
            if ($_.Exception.Message -like 'Duplicate Equation.DSMT4 table number detected:*') {
                throw
            }
        }
    }
    return [pscustomobject]@{
        shapes = @($shapes)
        by_number = $byNumber
    }
}

function Get-InventoryShapeForNumber {
    param(
        [Parameter(Mandatory = $true)]$Inventory,
        [Parameter(Mandatory = $true)][string]$Number
    )

    if ($Inventory.by_number.ContainsKey($Number)) {
        return $Inventory.by_number[$Number]
    }
    return $null
}

function Get-FormulaShapeForNumber {
    param(
        [Parameter(Mandatory = $true)]$Document,
        [Parameter(Mandatory = $true)][string]$Number
    )

    $matches = @()
    foreach ($shape in (Get-MathTypeShapes $Document)) {
        try {
            if ($shape.Range.Tables.Count -eq 1 -and
                [string]$shape.Range.Tables.Item(1).Range.Text -and
                $shape.Range.Tables.Item(1).Range.Text.Contains("($Number)")) {
                $matches += $shape
            }
        }
        catch {
        }
    }
    if ($matches.Count -gt 1) {
        throw "Expected at most one Equation.DSMT4 object for ($Number); found $($matches.Count)."
    }
    if ($matches.Count -eq 0) {
        return $null
    }
    return $matches[0]
}

function Get-FormulaOMathForNumber {
    param(
        [Parameter(Mandatory = $true)]$Document,
        [Parameter(Mandatory = $true)][string]$Number
    )

    $matches = @()
    for ($index = 1; $index -le $Document.OMaths.Count; $index++) {
        $equation = $Document.OMaths.Item($index)
        try {
            if ($equation.Range.Tables.Count -eq 1 -and
                [string]$equation.Range.Tables.Item(1).Range.Text -and
                $equation.Range.Tables.Item(1).Range.Text.Contains("($Number)")) {
                $matches += $equation
            }
        }
        catch {
        }
    }
    if ($matches.Count -gt 1) {
        throw "Expected at most one native OMML object for ($Number); found $($matches.Count)."
    }
    if ($matches.Count -eq 0) {
        return $null
    }
    return $matches[0]
}

function Get-MathTypeShapeInTable {
    param([Parameter(Mandatory = $true)]$Table)

    $matches = @()
    for ($index = 1; $index -le $Table.Range.InlineShapes.Count; $index++) {
        $shape = $Table.Range.InlineShapes.Item($index)
        try {
            if ([string]$shape.OLEFormat.ProgID -eq 'Equation.DSMT4') {
                $matches += $shape
            }
        }
        catch {
        }
    }
    if ($matches.Count -ne 1) {
        throw "Expected one Equation.DSMT4 object in the cloned formula table; found $($matches.Count)."
    }
    return $matches[0]
}

function Get-TableAtStart {
    param(
        [Parameter(Mandatory = $true)]$Document,
        [Parameter(Mandatory = $true)][int]$Start
    )

    $matches = @()
    for ($index = 1; $index -le $Document.Tables.Count; $index++) {
        $table = $Document.Tables.Item($index)
        if ([Math]::Abs([int]$table.Range.Start - $Start) -le 2) {
            $matches += $table
        }
    }
    if ($matches.Count -ne 1) {
        throw "Expected one newly inserted formula table at $Start; found $($matches.Count)."
    }
    return $matches[0]
}

function Set-EquationNumber {
    param(
        [Parameter(Mandatory = $true)]$Document,
        [Parameter(Mandatory = $true)]$Table,
        [Parameter(Mandatory = $true)]$Record
    )

    if ($Table.Rows.Count -ne 1 -or $Table.Columns.Count -ne 2) {
        throw 'MathType formula table must remain one row by two columns.'
    }
    $rightCell = $Table.Cell(1, 2)
    $fields = $rightCell.Range.Fields
    if ($fields.Count -ne 2) {
        throw "Equation number cell needs two fields; found $($fields.Count)."
    }
    $fields.Item(1).Code.Text = ' SEQ Chapter \c '
    $fields.Item(2).Code.Text = " SEQ Equation \r $([int]$Record.sequence) \* ARABIC "
    for ($index = 1; $index -le $fields.Count; $index++) {
        $fields.Item($index).Update()
    }

    $suffix = [string]$Record.suffix
    if (-not [string]::IsNullOrEmpty($suffix)) {
        $insertionStart = [int]$rightCell.Range.End - 2
        $Document.Range($insertionStart, $insertionStart).Text = $suffix
    }
    $visible = ([string]$rightCell.Range.Text).Replace("`r", '').Replace([char]7, '')
    $expected = "($([string]$Record.expected_number))"
    if ($visible -ne $expected) {
        throw "Inserted equation number is '$visible'; expected '$expected'."
    }
}

function Get-TextSha256 {
    param([Parameter(Mandatory = $true)][string]$Value)

    $hash = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
        return ([System.BitConverter]::ToString($hash.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $hash.Dispose()
    }
}

function Close-ComObject {
    param($Object)

    if ($null -ne $Object -and [System.Runtime.InteropServices.Marshal]::IsComObject($Object)) {
        try {
            [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($Object) | Out-Null
        }
        catch {
        }
    }
}

$sourcePath = Resolve-ExistingPath $Source
$manifestPath = Resolve-ExistingPath $Manifest
$outputPath = [System.IO.Path]::GetFullPath($Output)
$auditPath = [System.IO.Path]::GetFullPath($Audit)
if ([string]::IsNullOrWhiteSpace($ProgressLog)) {
    $ProgressLog = "$auditPath.progress.jsonl"
}
$progressPath = [System.IO.Path]::GetFullPath($ProgressLog)
if ($SaveEvery -lt 1) {
    throw 'SaveEvery must be at least 1.'
}
if ($sourcePath -eq $outputPath) {
    throw 'Output must be a new review copy; the authoritative source is immutable.'
}
if (Test-Path -LiteralPath $outputPath) {
    throw "Refusing to overwrite existing output: $outputPath"
}
if (Test-Path -LiteralPath $auditPath) {
    throw "Refusing to overwrite existing audit: $auditPath"
}
if (Test-Path -LiteralPath $progressPath) {
    throw "Refusing to overwrite existing progress log: $progressPath"
}

$allRecords = @(Get-ManifestRecords $manifestPath)
$recordsToWrite = @(Select-FormulaRecords $allRecords $FormulaId)
if ($recordsToWrite.Count -eq 0) {
    throw 'No formulas were selected for backend conversion.'
}

$plan = [ordered]@{
    schema = 'mosim.report.mathtype_mathml_backend.v1'
    mode = if ($Execute) { 'execute' } else { 'dry_run' }
    engine = 'Equation.DSMT4_OLE_IDataObject_MathML'
    source = $sourcePath
    source_sha256 = Get-Sha256 $sourcePath
    manifest = $manifestPath
    manifest_sha256 = Get-Sha256 $manifestPath
    output = $outputPath
    audit = $auditPath
    progress_log = $progressPath
    save_every = $SaveEvery
    requested_formula_ids = @($recordsToWrite | ForEach-Object { [int]$_.formula_id })
    requested_formula_count = $recordsToWrite.Count
    full_document_requested = ($recordsToWrite.Count -eq 104)
    foreground_interaction = $false
    selection_or_activation_used = $false
    clipboard_used = $false
    legacy_tex_toggle_used = $false
    required_precondition = 'No pre-existing WINWORD or MathType process may be running at execute time.'
    visual_acceptance = 'separate_render_and_review_gate'
}

if (-not $Execute) {
    $plan | ConvertTo-Json -Depth 8
    exit 0
}

$preexisting = @(Get-ProcessSnapshot)
if ($preexisting.Count -ne 0) {
    throw "Refusing backend conversion while Word or MathType is already running: $($preexisting | ConvertTo-Json -Compress)"
}
if (-not (Test-Path -LiteralPath $helperPath -PathType Leaf)) {
    throw "MathType OLE helper is missing: $helperPath"
}
if (-not ('MathTypeOleData' -as [type])) {
    Add-Type -Path $helperPath
}

$outputDirectory = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $auditPath) | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $progressPath) | Out-Null
Copy-Item -LiteralPath $sourcePath -Destination $outputPath -ErrorAction Stop

$word = $null
$document = $null
$verifyWord = $null
$verifyDocument = $null
$rawOleObject = $null
$writes = @()
$status = 'failed'
$failure = $null
$initialMathType = $null
$initialOmml = $null
$finalMathType = $null
$finalOmml = $null
$newConversions = 0
$updatedExisting = 0
$classification = @()
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.ScreenUpdating = $false
    $document = $word.Documents.Open($outputPath, $false, $false, $false)

    $inventory = Get-MathTypeInventory $document
    $mathTypeShapes = @($inventory.shapes)
    $initialMathType = $mathTypeShapes.Count
    $initialOmml = [int]$document.OMaths.Count
    if ($initialMathType -lt 1) {
        throw 'Source report has no Equation.DSMT4 donor object.'
    }
    if ($initialMathType + $initialOmml -ne 104) {
        throw "Source object inventory must contain 104 display equations; observed MathType=$initialMathType OMML=$initialOmml."
    }

    # Classify the current candidate before editing.  Existing OLE objects are
    # updated in place; only the remaining native OMML objects are replaced.
    # This prevents duplicate formula tables when a prior review pass already
    # converted part of the report.
    $existingById = @{}
    $shapeById = @{}
    $pendingRecords = @()
    foreach ($candidateRecord in $allRecords) {
        $candidateId = [int]$candidateRecord.formula_id
        $existingShape = Get-InventoryShapeForNumber $inventory ([string]$candidateRecord.expected_number)
        if ($null -eq $existingShape) {
            $pendingRecords += $candidateRecord
        }
        else {
            $existingById[$candidateId] = $true
            $shapeById[$candidateId] = $existingShape
        }
    }
    $pendingRecords = @($pendingRecords)
    if ($pendingRecords.Count -ne $initialOmml) {
        throw "Formula classification found $($pendingRecords.Count) pending records, but Word exposes $initialOmml OMML objects."
    }
    $nativeIndexById = @{}
    for ($pendingIndex = 0; $pendingIndex -lt $pendingRecords.Count; $pendingIndex++) {
        $nativeIndexById[[int]$pendingRecords[$pendingIndex].formula_id] = $pendingIndex + 1
    }
    foreach ($candidateRecord in $allRecords) {
        $candidateId = [int]$candidateRecord.formula_id
        $classification = @($classification + [ordered]@{
            formula_id = $candidateId
            expected_number = [string]$candidateRecord.expected_number
            current_object = if ($existingById.ContainsKey($candidateId)) { 'Equation.DSMT4' } else { 'OMML' }
            native_omath_index = if ($nativeIndexById.ContainsKey($candidateId)) { [int]$nativeIndexById[$candidateId] } else { $null }
        })
    }

    $expectedMathType = $initialMathType
    $expectedOmml = $initialOmml
    foreach ($record in $recordsToWrite) {
        $formulaId = [int]$record.formula_id
        $number = [string]$record.expected_number
        $action = 'updated_existing_ole'
        if ($existingById.ContainsKey($formulaId)) {
            $target = $shapeById[$formulaId]
            if ($null -eq $target) {
                throw "Formula ($number) was classified as OLE but could not be found again."
            }
            $updatedExisting += 1
        }
        else {
            if (-not $nativeIndexById.ContainsKey($formulaId)) {
                throw "Formula ($number) has no native OMML index in the current candidate."
            }
            $currentNativeIndex = [int]$nativeIndexById[$formulaId] - $newConversions
            if ($currentNativeIndex -lt 1 -or $currentNativeIndex -gt $document.OMaths.Count) {
                throw "Computed native OMML index $currentNativeIndex is invalid for ($number)."
            }
            $targetOmml = $document.OMaths.Item($currentNativeIndex)
            $inExistingTable = $targetOmml.Range.Tables.Count -gt 0
            if ($inExistingTable) {
                $targetTable = $targetOmml.Range.Tables.Item(1)
                $donor = $mathTypeShapes[0]
                $donorRange = $donor.Range.Duplicate
                $insertionStart = [int]$targetOmml.Range.Start
                $targetOmml.Range.Delete()
                $insertion = $document.Range($insertionStart, $insertionStart)
                $insertion.FormattedText = $donorRange.FormattedText
                $target = Get-MathTypeShapeInTable $targetTable
                $action = 'replaced_table_omml'
            }
            else {
                $donor = $mathTypeShapes[0]
                $donorTable = $donor.Range.Tables.Item(1)
                $donorTableRange = $donorTable.Range.Duplicate
                $targetParagraph = $targetOmml.Range.Paragraphs.Item(1).Range
                $insertionStart = [int]$targetParagraph.Start
                $targetParagraph.Delete()
                $insertion = $document.Range($insertionStart, $insertionStart)
                $insertion.FormattedText = $donorTableRange.FormattedText
                $insertedTable = Get-TableAtStart $document $insertionStart
                Set-EquationNumber $document $insertedTable $record
                $target = Get-MathTypeShapeInTable $insertedTable
                $action = 'replaced_standalone_omml_with_table'
            }
            if ($null -eq $target) {
                throw "Word did not expose the new Equation.DSMT4 object for ($number)."
            }
            $expectedOmml -= 1
            $expectedMathType += 1
            $newConversions += 1
        }

        $target.OLEFormat.DoVerb(2)
        $rawOleObject = $target.OLEFormat.Object
        $beforeMathMl = [MathTypeOleData]::GetPresentationMathML($rawOleObject)
        [MathTypeOleData]::SetPresentationMathML($rawOleObject, [string]$record.mathml)
        $roundTripMathMl = [MathTypeOleData]::GetPresentationMathML($rawOleObject)
        if (-not $roundTripMathMl.Trim().StartsWith('<math')) {
            throw "MathType readback for ($number) did not return a MathML root."
        }
        [MathTypeOleData]::CloseWithoutSave($rawOleObject)
        $rawOleObject = $null

        $observedMathType = (Get-MathTypeShapes $document).Count
        $observedOmml = [int]$document.OMaths.Count
        if ($observedMathType -ne $expectedMathType -or $observedOmml -ne $expectedOmml) {
            throw "Object count mismatch for ($number): MathType=$observedMathType/$expectedMathType OMML=$observedOmml/$expectedOmml."
        }
        $writes = @($writes + [ordered]@{
            formula_id = $formulaId
            expected_number = $number
            expected_mathml_sha256 = [string]$record.mathml_sha256
            prior_mathml_sha256 = Get-TextSha256 $beforeMathMl
            round_trip_mathml_sha256 = Get-TextSha256 $roundTripMathMl
            object_type = [string]$target.OLEFormat.ProgID
            action = $action
            status = 'saved_backend_checkpoint'
        })
        if (($writes.Count % $SaveEvery) -eq 0) {
            $document.Save()
        }
        $progressRecord = [ordered]@{
            formula_id = $formulaId
            expected_number = $number
            action = $action
            completed = $writes.Count
            expected_math_type = $expectedMathType
            expected_omml = $expectedOmml
        }
        Add-Content -LiteralPath $progressPath -Value ($progressRecord | ConvertTo-Json -Compress) -Encoding UTF8
    }

    $document.Save()
    $document.Close($false)
    Close-ComObject $document
    $document = $null
    $word.Quit($false)
    Close-ComObject $word
    $word = $null

    # Structural acceptance comes from a fresh hidden Word instance.
    $verifyWord = New-Object -ComObject Word.Application
    $verifyWord.Visible = $false
    $verifyWord.DisplayAlerts = 0
    $verifyWord.ScreenUpdating = $false
    $verifyDocument = $verifyWord.Documents.Open($outputPath, $false, $true, $false)
    $finalInventory = Get-MathTypeInventory $verifyDocument
    $finalMathType = @($finalInventory.shapes).Count
    $finalOmml = [int]$verifyDocument.OMaths.Count
    $fullCountFailure = $plan.full_document_requested -and
        ($finalMathType -ne 104 -or $finalOmml -ne 0)
    if ($fullCountFailure -or $finalMathType -ne $expectedMathType -or $finalOmml -ne $expectedOmml) {
        throw "Fresh Word reopen count mismatch: MathType=$finalMathType/$expectedMathType OMML=$finalOmml/$expectedOmml."
    }
    foreach ($record in $recordsToWrite) {
        if (-not $finalInventory.by_number.ContainsKey([string]$record.expected_number)) {
            throw "Fresh Word reopen has no numbered Equation.DSMT4 object for ($($record.expected_number))."
        }
    }
    $verifyDocument.Close($false)
    Close-ComObject $verifyDocument
    $verifyDocument = $null
    $verifyWord.Quit($false)
    Close-ComObject $verifyWord
    $verifyWord = $null
    if ($plan.full_document_requested) {
        $status = 'passed_hidden_structural_reopen_pending_visual_review'
    }
    else {
        $status = 'passed_partial_hidden_structural_reopen_pending_visual_review'
    }
}
catch {
    $failure = "{0}: {1}" -f $_.Exception.GetType().FullName, $_.Exception.Message
    throw
}
finally {
    if ($null -ne $rawOleObject) {
        try { [MathTypeOleData]::CloseWithoutSave($rawOleObject) } catch {}
    }
    if ($null -ne $document) {
        try { $document.Close($false) } catch {}
        Close-ComObject $document
    }
    if ($null -ne $word) {
        try { $word.Quit($false) } catch {}
        Close-ComObject $word
    }
    if ($null -ne $verifyDocument) {
        try { $verifyDocument.Close($false) } catch {}
        Close-ComObject $verifyDocument
    }
    if ($null -ne $verifyWord) {
        try { $verifyWord.Quit($false) } catch {}
        Close-ComObject $verifyWord
    }

    $auditPayload = [ordered]@{}
    foreach ($item in $plan.GetEnumerator()) { $auditPayload[$item.Key] = $item.Value }
    $auditPayload['status'] = $status
    $auditPayload['failure'] = $failure
    $auditPayload['writes'] = $writes
    $auditPayload['classification'] = $classification
    $auditPayload['new_omml_replacements'] = $newConversions
    $auditPayload['existing_ole_updates'] = $updatedExisting
    $auditPayload['initial_object_counts'] = @{ mathtype = $initialMathType; omml = $initialOmml }
    $auditPayload['final_object_counts'] = @{ mathtype = $finalMathType; omml = $finalOmml }
    $auditPayload['output_exists'] = Test-Path -LiteralPath $outputPath -PathType Leaf
    $auditPayload['output_sha256'] = if ($auditPayload['output_exists']) { Get-Sha256 $outputPath } else { $null }
    $auditPayload['remaining_word_mathtype_processes'] = @(Get-ProcessSnapshot)
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $auditPath) | Out-Null
    $auditPayload | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $auditPath -Encoding UTF8
}

$auditPayload | ConvertTo-Json -Depth 10
