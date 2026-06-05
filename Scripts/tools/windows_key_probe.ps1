Write-Host "Windows key probe"
Write-Host "Press these keys in order: a, Backspace, Delete, Enter, Ctrl+V, Esc"
Write-Host "Each key event will be printed below. Esc exits early."

for ($i = 0; $i -lt 20; $i++) {
    $k = [Console]::ReadKey($true)
    $charCode = [int][char]$k.KeyChar
    "{0:HH:mm:ss} Key={1} CharCode={2} Modifiers={3}" -f (Get-Date), $k.Key, $charCode, $k.Modifiers
    if ($k.Key -eq [ConsoleKey]::Escape) {
        break
    }
}
