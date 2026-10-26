param(
    [string]$LogDir = "work\nightly",
    [switch]$Full
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

Say "== smoke (quest flow) =="
if ($Full) {
    & python work\smoke_test.py --full --plus 2>&1 | Tee-Object -FilePath $log -Append
} else {
    & python work\smoke_test.py --plus 2>&1 | Tee-Object -FilePath $log -Append
}
try {
    $smoke = Get-Content tests\smoke\latest.json -Raw | ConvertFrom-Json
    if ($smoke.status -ne "PASS") {
        $ok = $false
        Say "smoke status: $($smoke.status)"
    }
} catch {
    $ok = $false
    Say "smoke status: unreadable ($_)"
}

Say "== BOTS sweep =="
& python work\sweep_bots59.py 2>&1 | Tee-Object -FilePath $log -Append
try {
    $sweep = Get-Content tests\sweep\sweep_59.json -Raw | ConvertFrom-Json
    $count = @($sweep.results).Count
    Say "BOTS sweep count: $count/59"
    if ($count -lt 59) {
        $partial = $true
        Say "BOTS sweep: PARTIAL ($count/59)"
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
