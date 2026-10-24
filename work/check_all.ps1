param([switch]$SkipSmoke)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $Root "..")
$results = @()
$results += "== golden =="
& python work\golden_regression.py; $g = $LASTEXITCODE; $results += "golden_exit=$g"
if (-not $SkipSmoke) {
    $results += "== smoke (fast) =="
    & python work\smoke_test.py --plus --fight; $s = $LASTEXITCODE; $results += "smoke_exit=$s"
} else { $s = 0 }
$results += "== unittest =="
& python -m unittest discover -s tests -p "test_*.py" -v; $u = $LASTEXITCODE; $results += "unittest_exit=$u"
$results | ForEach-Object { Write-Host $_ }
$ok = ($g -eq 0) -and ($s -eq 0) -and ($u -eq 0)
Write-Host ("VERDICT: " + $(if ($ok) { "PASS" } else { "FAIL" }))
if (-not $ok) { exit 1 }
