[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')]
    [string]$ThreadId,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$RolloutPath,

    [ValidateRange(1, 5000)]
    [int]$MaxRecordsAfterCompaction = 240
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function ConvertTo-Record {
    param([Parameter(Mandatory)][string]$Line)

    try {
        return $Line | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return $null
    }
}

function Get-RecordValue {
    param(
        [Parameter(Mandatory)][object]$Record,
        [Parameter(Mandatory)][string]$Name
    )

    if ($Record -is [System.Collections.IDictionary]) {
        return $Record[$Name]
    }
    $property = $Record.PSObject.Properties[$Name]
    if ($property) {
        return $property.Value
    }
    return $null
}

function Complete-Sample {
    param(
        [Parameter(Mandatory)][hashtable]$Sample,
        [Parameter(Mandatory)][string]$Reason
    )

    $Sample['end_reason'] = $Reason
    $hasHookEvidence = $Sample['hook_prompt_event_after'] -or $Sample['hook_signature_after']
    if ($hasHookEvidence) {
        $Sample['classification'] = 'hook_present_observation'
    }
    elseif (-not $Sample['turn_context_after']) {
        $Sample['classification'] = 'no_continuation_request_observed'
    }
    elseif ($Sample['task_complete_after'] -and $Sample['final_answer_after']) {
        $Sample['classification'] = 'model_final_then_task_complete'
    }
    elseif ($Sample['task_complete_after']) {
        $Sample['classification'] = 'task_complete_without_final_answer_observed'
    }
    else {
        $Sample['classification'] = 'continued_without_terminal_event_in_window'
    }
    return [pscustomobject]$Sample
}

$resolvedRollout = (Resolve-Path -LiteralPath $RolloutPath).Path
$samples = [System.Collections.Generic.List[object]]::new()
$active = $null
$lineNumber = 0

# Codex keeps the active rollout open. ReadWrite sharing avoids changing the
# client lock state while still giving this audit a coherent event stream.
$stream = [System.IO.FileStream]::new(
    $resolvedRollout,
    [System.IO.FileMode]::Open,
    [System.IO.FileAccess]::Read,
    [System.IO.FileShare]::ReadWrite
)

try {
    $reader = [System.IO.StreamReader]::new(
        $stream,
        [System.Text.UTF8Encoding]::new($false),
        $true,
        65536,
        $true
    )
    try {
        while (($line = $reader.ReadLine()) -ne $null) {
            $lineNumber++

            if ($line -match '"type":"compacted"') {
                $record = ConvertTo-Record -Line $line
                if ($record -and (Get-RecordValue -Record $record -Name 'type') -eq 'compacted') {
                    if ($active) {
                        $samples.Add((Complete-Sample -Sample $active -Reason 'next_compaction'))
                    }
                    $active = @{
                        compact_line = $lineNumber
                        compact_timestamp = Get-RecordValue -Record $record -Name 'timestamp'
                        records_after = 0
                        hook_prompt_event_after = $false
                        hook_signature_after = $false
                        turn_context_after = $false
                        assistant_message_after = $false
                        final_answer_after = $false
                        task_complete_after = $false
                        user_message_after = $false
                    }
                    continue
                }
            }

            if (-not $active) {
                continue
            }

            $active['records_after']++
            if ($line -match '"type":"hookPrompt"') {
                $active['hook_prompt_event_after'] = $true
            }
            if ($line -match 'MoSim native Codex hook active') {
                $active['hook_signature_after'] = $true
            }

            $isInteresting = $line -match '"type":"turn_context"' -or
                $line -match '"type":"agent_message"' -or
                $line -match '"type":"task_complete"' -or
                $line -match '"type":"user_message"' -or
                $line -match '"role":"assistant"'

            if ($isInteresting) {
                $record = ConvertTo-Record -Line $line
                if ($record) {
                    $payload = Get-RecordValue -Record $record -Name 'payload'
                    if ((Get-RecordValue -Record $record -Name 'type') -eq 'turn_context') {
                        $active['turn_context_after'] = $true
                    }
                    elseif ($payload) {
                        if ((Get-RecordValue -Record $payload -Name 'type') -eq 'agent_message') {
                            $active['assistant_message_after'] = $true
                            if ((Get-RecordValue -Record $payload -Name 'phase') -eq 'final_answer') {
                                $active['final_answer_after'] = $true
                            }
                        }
                        elseif ((Get-RecordValue -Record $payload -Name 'type') -eq 'task_complete') {
                            $active['task_complete_after'] = $true
                        }
                        elseif ((Get-RecordValue -Record $payload -Name 'type') -eq 'user_message') {
                            $active['user_message_after'] = $true
                            $samples.Add((Complete-Sample -Sample $active -Reason 'next_user_message'))
                            $active = $null
                            continue
                        }

                        if ((Get-RecordValue -Record $payload -Name 'role') -eq 'assistant') {
                            $active['assistant_message_after'] = $true
                            if ((Get-RecordValue -Record $payload -Name 'phase') -eq 'final_answer') {
                                $active['final_answer_after'] = $true
                            }
                        }
                    }
                }
            }

            if ($active -and $active['records_after'] -ge $MaxRecordsAfterCompaction) {
                $samples.Add((Complete-Sample -Sample $active -Reason 'record_limit'))
                $active = $null
            }
        }
    }
    finally {
        $reader.Dispose()
    }
}
finally {
    $stream.Dispose()
}

if ($active) {
    $samples.Add((Complete-Sample -Sample $active -Reason 'end_of_file'))
}

$noHookSamples = @($samples | Where-Object {
    -not $_.hook_prompt_event_after -and -not $_.hook_signature_after
})
$result = [ordered]@{
    schema = 'mosim.codex_compaction_lifecycle.v1'
    thread_id = $ThreadId
    rollout_path = $resolvedRollout
    observed_at = (Get-Date).ToUniversalTime().ToString('o')
    max_records_after_compaction = $MaxRecordsAfterCompaction
    scanned_lines = $lineNumber
    compaction_count = $samples.Count
    no_hook_sample_count = $noHookSamples.Count
    no_hook_no_continuation_request_count = @($noHookSamples | Where-Object {
        $_.classification -eq 'no_continuation_request_observed'
    }).Count
    no_hook_model_final_then_complete_count = @($noHookSamples | Where-Object {
        $_.classification -eq 'model_final_then_task_complete'
    }).Count
    samples = @($samples)
}

$result | ConvertTo-Json -Depth 5
