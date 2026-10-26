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
$partial = $false

Say "== check_all (golden + fast smoke + unittest) =="
$checkOut = & powershell -ExecutionPolicy Bypass -File work\check_all.ps1 2>&1
$checkOut | Tee-Object -FilePath $log -Append
if (-not ($checkOut -match "VERDICT: PASS")) { $ok = $false }

Say "== full smoke (--full --plus) =="
& python work\smoke_test.py --full --plus 2>&1 | Tee-Object -FilePath $log -Append
try {
    $smoke = Get-Content tests\smoke\latest.json -Raw | ConvertFrom-Json
    if ($smoke.status -ne "PASS") {
        $ok = $false
        Say "full smoke status: $($smoke.status)"
    }
} catch {
    $ok = $false
    Say "full smoke status: unreadable ($_)"
}

Say "== BOTS sweep =="
& python work\sweep_bots.py 2>&1 | Tee-Object -FilePath $log -Append
try {
    $sweep = Get-Content tests\sweep\sweep_12.json -Raw | ConvertFrom-Json
    $count = @($sweep).Count
    Say "BOTS sweep count: $count/59"
    if ($count -lt 59) {
        $partial = $true
        Say "BOTS sweep: PARTIAL ($count/59; the script currently covers the first 12 cards)"
    }
} catch {
    $partial = $true
    Say "BOTS sweep: no result file ($_)"
}

Say "== summary =="
if (-not $ok) { Say "VERDICT: FAIL" }
elseif ($partial) { Say "VERDICT: PARTIAL" }
else { Say "VERDICT: PASS" }
Say "log: $log"
if (-not $ok) { exit 1 }
if ($partial) { exit 2 }
