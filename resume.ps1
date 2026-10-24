# Resume the TFTF 9.2.0 offline stack in one command.
# Usage:  .\resume.ps1 [-Full] [-NoSmoke] [-NoGolden]
param(
    [switch]$Full,
    [switch]$NoSmoke,
    [switch]$NoGolden
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Adb = Join-Path $Root "work\platform-tools\adb.exe"
$Pkg = "com.kabam.bigrobot"
$Activity = "com.kabam.bigrobot/com.explodingbarrel.Activity"
$Apk = Get-ChildItem $Root -Filter "com.kabam.bigrobot_9.2.0*.apk" | Select-Object -First 1

Write-Host "== TFTF resume ==" -ForegroundColor Cyan
Write-Host "root: $Root"

if (-not (Test-Path $Adb)) { throw "adb not found: $Adb" }

# 1. Emulator / device
$devices = & $Adb devices
if ($devices -notmatch "emulator-\d+\s+device") {
    throw "No emulator device. Start TFTF_AVD first, then rerun."
}
Write-Host "device: OK" -ForegroundColor Green

# 2. Port reverse
& $Adb reverse tcp:8080 tcp:8080 | Out-Null
Write-Host "adb reverse tcp:8080: OK" -ForegroundColor Green

# 3. Stub server
$listening = $false
try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8080/auth/init" -TimeoutSec 3
    $listening = ($resp.StatusCode -eq 200)
} catch { $listening = $false }
if (-not $listening) {
    Write-Host "starting stub server on 8080..."
    Start-Process -FilePath "python" -ArgumentList "server\stub_server.py", "8080" -WorkingDirectory $Root -WindowStyle Minimized
    Start-Sleep -Seconds 3
    try {
        $resp = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8080/auth/init" -TimeoutSec 5
        $listening = ($resp.StatusCode -eq 200)
    } catch { $listening = $false }
}
if (-not $listening) { throw "stub server did not answer on 127.0.0.1:8080" }
Write-Host "stub server: OK" -ForegroundColor Green

# 4. Installed APK / hash
$version = (& $Adb shell dumpsys package $Pkg | Select-String -Pattern "versionName=" | Select-Object -First 1).ToString().Trim()
Write-Host "installed: $version"
if ($Apk) {
    $hash = (Get-FileHash $Apk.FullName -Algorithm SHA256).Hash.ToLower()
    Write-Host "apk: $($Apk.Name)"
    Write-Host "sha256: $hash"
    if ($hash -ne "77d2e9dd833c3789db541e04af08082547603b5815be28cf5f5d0c68173763cb") {
        Write-Warning "APK hash differs from the documented original 9.2.0 hash."
    }
} else {
    Write-Warning "Original APK not found in project root."
}

# 5. Optional launch
$running = & $Adb shell pidof $Pkg
if (-not $running) {
    Write-Host "launching $Activity"
    & $Adb shell am start -n $Activity | Out-Null
} else {
    Write-Host "app already running (pid $running)"
}

# 6. Fast/full smoke
if (-not $NoSmoke) {
    $args = @("work\smoke_test.py")
    if ($Full) { $args += "--full" }
    & python @args
    if ($LASTEXITCODE -ne 0) { Write-Warning "smoke_test.py exited $LASTEXITCODE" }
}

# 7. Golden regression
if (-not $NoGolden) {
    & python "work\golden_regression.py"
    if ($LASTEXITCODE -ne 0) { Write-Warning "golden_regression.py exited $LASTEXITCODE (re-record if shapes intentionally changed)" }
}

Write-Host "== done ==" -ForegroundColor Cyan
