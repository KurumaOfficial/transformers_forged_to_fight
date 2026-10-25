param(
    [Parameter(Mandatory=$true)][string]$Destination
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $Root "..")
$stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$out = Join-Path $Destination "TFTF_project_$stamp.zip"
$include = @("server","spec","docs","data","tests","report","work","notes","README_RESUME.md","MASTER_PROMPT.md","STATE.md","FIDELITY.md","COVERAGE_WIKI.md","OPEN_QUESTIONS.md","LEDGER.md","resume.ps1")
$stage = Join-Path $env:TEMP "tftf_backup_$stamp"
if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Force -Path $stage | Out-Null
foreach ($rel in $include) {
    $src = Join-Path (Get-Location) $rel
    if (Test-Path $src) {
        $dst = Join-Path $stage $rel
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
        Copy-Item -Recurse -Force $src $dst
    }
}
Get-ChildItem $stage -Recurse -File | Where-Object {
    $_.Extension -in ".apk",".zip" -or
    $_.FullName -match "\\unpacked\\|\\il2cpp_dump\\|\\android-sdk\\|\\platform-tools\\|\\__pycache__\\|\\.git\\"
} | Remove-Item -Force
if (-not (Test-Path $Destination)) { New-Item -ItemType Directory -Force -Path $Destination | Out-Null }
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $out -CompressionLevel Optimal
$hash = (Get-FileHash $out -Algorithm SHA256).Hash.ToLower()
Remove-Item -Recurse -Force $stage
Write-Host "backup: $out"
Write-Host "sha256: $hash"
