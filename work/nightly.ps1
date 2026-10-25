param(
    [string]$LogDir = "work\nightly"
)
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $Root "..")
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$log = Join-Path $LogDir "nightly_$stamp.log"
function Say($text) { $text | Tee-Object -FilePath $log -Append }
Say "== TFTF nightly $stamp =="
$ok = $true

Say "== check_all (golden + fast smoke + unittest) =="
& powershell -ExecutionPolicy Bypass -File work\check_all.ps1 2>&1 | Tee-Object -FilePath $log -Append
if ($LASTEXITCODE -ne 0) { $ok = $false }

Say "== full smoke (--full --plus) =="
& python work\smoke_test.py --full --plus 2>&1 | Tee-Object -FilePath $log -Append
if ($LASTEXITCODE -ne 0) { $ok = $false }

Say "== BOTS sweep =="
& python work\sweep_bots.py 2>&1 | Tee-Object -FilePath $log -Append
if ($LASTEXITCODE -ne 0) { $ok = $false }

Say "== summary =="
Say ("PASS" | ForEach-Object { if ($ok) { "VERDICT: PASS" } else { "VERDICT: FAIL" } })
Say "log: $log"
if (-not $ok) { exit 1 }
