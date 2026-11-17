# Plays the probe schedule (plan.py) in real R5 Flowstate and saves the per-tick log to out\r5f.log.
# Local dedicated server (Firing Range, +hostname r5rust_probe) + one windowed client that plays the plan itself
# through the engine's own +forward/+jump commands (no focus or SendInput needed). The mod is installed for the
# run and removed afterwards. Launch recipe copied from apex\lurch-trainer\r5test\run.ps1.
#   .\tools\r5f-probe\run.ps1            run everything, then compare: cargo run --release -p shared --example probecmp
#   .\tools\r5f-probe\run.ps1 -Stop      kill a stuck run
param([string]$Game = "$env:USERPROFILE\Games\R5Flowstate", [int]$Port = 37121, [int]$TickRate = 60, [switch]$Stop, [switch]$KeepMod, [switch]$Shots)
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$out = Join-Path $here 'out'; New-Item -ItemType Directory -Force $out | Out-Null
$pidFile = Join-Path $out 'pids.txt'
$id = 'Kainz.R5RustProbe'
$dst = Join-Path $Game 'mods\Kainz-R5RustProbe'
$vdf = Join-Path $Game 'mods\mods.vdf'
function Stop-Run {
    if (Test-Path $pidFile) { Get-Content $pidFile | ForEach-Object { try { Stop-Process -Id ([int]$_) -Force -ErrorAction Stop } catch {} }; Remove-Item $pidFile }
}
function Remove-Mod {
    if (Test-Path $dst) { Remove-Item -LiteralPath $dst -Recurse -Force }
    @(Get-Content $vdf) | Where-Object { $_ -notmatch [regex]::Escape("`"$id`"") } | Set-Content $vdf
}
if ($Stop) { Stop-Run; Remove-Mod; 'stopped'; return }

# install
Remove-Mod
Copy-Item -Recurse (Join-Path $here 'mod\Kainz-R5RustProbe') $dst
$lines = @(Get-Content $vdf)
$close = [array]::LastIndexOf($lines, '}')
($lines[0..($close - 1)] + "`t`"$id`"`t`"1`"" + $lines[$close..($lines.Count - 1)]) | Set-Content $vdf

try {
    $inv = [Globalization.CultureInfo]::InvariantCulture
    $srvArgs = @('-dedicated', '-logfiles', '-port', $Port, '+sv_allowSendTableTransmitToClients', '1', '+stringtable_compress', '1',
        '+spire_host_visibility', '0', '+sv_cheats', '1', '+launchplaylist', 'survival_firingrange', '+map', 'mp_rr_canyonlands_staging_mu1',
        '+sv_modPolicy', '0', '+base_tickinterval_mp', (1.0 / $TickRate).ToString($inv), '+sv_updaterate_mp', $TickRate,
        '+sv_maxupdaterate', $TickRate, '+hostname', 'r5rust_probe')
    $started = Get-Date
    $ds = Start-Process (Join-Path $Game 'r5apex_ds.exe') -WorkingDirectory $Game -PassThru -WindowStyle Minimized -ArgumentList $srvArgs
    $ds.Id | Set-Content $pidFile
    "server pid $($ds.Id) on port $Port"
    $logRoot = Join-Path $Game 'platform\logs\server'
    $deadline = (Get-Date).AddSeconds(150)
    $latest = $null; $ready = $false
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 1000
        if ($ds.HasExited) { throw "server exited ($($ds.ExitCode))" }
        $latest = Get-ChildItem $logRoot -Directory | Where-Object { $_.CreationTime -gt $started.AddSeconds(-5) } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if (-not $latest) { continue }
        if ((Get-Content (Join-Path $latest.FullName 'script.log') -Raw -ErrorAction SilentlyContinue) -match '\[RPROBE\] server ready') {
            if (Get-NetUDPEndpoint -LocalPort $Port -ErrorAction SilentlyContinue) { $ready = $true; break }
        }
        $err = Get-Content (Join-Path $latest.FullName 'error.log') -Raw -ErrorAction SilentlyContinue
        if ($err -match 'COMPILE ERROR|Refusing the mod') { throw "server refused/failed the probe mod: $($latest.FullName)\error.log" }
    }
    if (-not $ready) { throw 'server never reported [RPROBE] server ready' }
    $log = Join-Path $latest.FullName 'script.log'
    "server log: $log"
    Start-Sleep 2
    $cl = Start-Process (Join-Path $Game 'r5apex_dx12.exe') -WorkingDirectory $Game -PassThru `
        -ArgumentList '-nodiscord', '-logfiles', '-allowmultiple', '+timeout_during_load', '600', '-language', 'english',
        '+miles_language', 'english', '-windowed', '-noborder', '-width', 1280, '-height', 720, '+cl_updaterate_mp', $TickRate, '+connect', "127.0.0.1:$Port"
    $cl.Id | Add-Content $pidFile
    # a background window gets EcoQoS-throttled to ~8 fps, and every usercmd then carries a 1/8 s frametime, which
    # changes the physics: opt the client out of power throttling and raise its priority
    Add-Type -Namespace R5P -Name Native -MemberDefinition @'
[DllImport("kernel32.dll")] public static extern IntPtr OpenProcess(uint access, bool inherit, int pid);
[DllImport("kernel32.dll")] public static extern bool SetProcessInformation(IntPtr h, int cls, int[] info, int size);
'@
    $h = [R5P.Native]::OpenProcess(0x0200, $false, $cl.Id)   # PROCESS_SET_INFORMATION
    $ok = [R5P.Native]::SetProcessInformation($h, 4, @(1, 1, 0), 12)   # ProcessPowerThrottling: version 1, EXECUTION_SPEED off
    try { $cl.PriorityClass = 'High' } catch {}
    "power throttling off: $ok"
    "client pid $($cl.Id); waiting for the plan to finish"
    $deadline = (Get-Date).AddSeconds(600)
    $shotDir = Join-Path $out 'shots'; $seen = 0; $cdir = $null
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 250
        if ($Shots) {
            # screenshot on every "[RPROBE] shot <name>" the client prints (PrintWindow on its PID, no focus needed)
            # the probe client's own log (another R5F session may be writing logs at the same time)
            if (-not $cdir) { $cdir = Get-ChildItem (Join-Path $Game 'platform\logs\client') -Directory | Where-Object { $_.CreationTime -gt $started } | Where-Object { Select-String -Path (Join-Path $_.FullName 'script.log') -Pattern '\[RPROBE\] client running' -Quiet -ErrorAction SilentlyContinue } | Select-Object -First 1 }
            if ($cdir) {
                $hits = @(Select-String -Path (Join-Path $cdir.FullName 'script.log') -Pattern '\[RPROBE\] shot (\S+)' -ErrorAction SilentlyContinue)
                for ($k = $seen; $k -lt $hits.Count; $k++) {
                    $nm = $hits[$k].Matches[0].Groups[1].Value
                    $ts = [datetime]::ParseExact($hits[$k].Line.Substring(1, 23), 'yyyy-MM-dd HH:mm:ss.fff', $null)
                    $lag = ((Get-Date) - $ts).TotalSeconds
                    if ($lag -gt 9.0) { "shot $nm skipped: log line seen $([math]::Round($lag, 1)) s late"; continue }
                    "shot $nm (log lag $([math]::Round($lag, 1)) s)"
                    python (Join-Path $here 'snap.py') (Join-Path $shotDir "$nm.png") --pid $cl.Id
                }
                $seen = $hits.Count
            }
        }
        if ($cl.HasExited) { throw "client exited ($($cl.ExitCode))" }
        $txt = Get-Content $log -Raw -ErrorAction SilentlyContinue
        if ($txt -match '\[RPROBE\] done') { break }
    }
    Copy-Item $log (Join-Path $out 'r5f.log') -Force
    if (-not $cdir) { $cdir = Get-ChildItem (Join-Path $Game 'platform\logs\client') -Directory | Where-Object { $_.CreationTime -gt $started } | Where-Object { Select-String -Path (Join-Path $_.FullName 'script.log') -Pattern '\[RPROBE\] client running' -Quiet -ErrorAction SilentlyContinue } | Select-Object -First 1 }
    if ($cdir) { Copy-Item (Join-Path $cdir.FullName 'script.log') (Join-Path $out 'r5f_client.log') -Force }
    $n = (Select-String -Path (Join-Path $out 'r5f.log') -Pattern '\[RPROBE\] s ').Count
    "saved out\r5f.log ($n samples)"
} finally {
    Stop-Run
    if (-not $KeepMod) { Remove-Mod }
}
