[CmdletBinding()]
param(
  [string]$Server = '192.168.0.200',
  [string]$User = 'unibell4',
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$hubBundle = Join-Path $repoRoot 'tmp\pj-general-web-working-tree.tgz'
$tasksBundle = Join-Path $repoRoot 'tmp\vikunja-listening-lounge-working-tree.tgz'
$hubSource = Join-Path $repoRoot 'apps\web'
$tasksSource = Join-Path $repoRoot 'tmp\vikunja-listening-lounge'
$startScript = Join-Path $PSScriptRoot 'start-pj-general.sh'
$remoteHelper = Join-Path $PSScriptRoot 'redeploy-p0-frontend-remote.sh'
$remote = "$User@$Server"

function Require-File([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "missing required file: $Path" }
}

function Require-Directory([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path -PathType Container)) { throw "missing required directory: $Path" }
}

function New-CurrentBundles {
  Require-Directory $hubSource
  Require-Directory $tasksSource

  & tar.exe -czf $hubBundle --exclude=apps/web/node_modules --exclude=apps/web/data/p0.sqlite --exclude=apps/web/__pycache__ -C $repoRoot apps/web
  if ($LASTEXITCODE -ne 0) { throw "Hub bundle creation failed with exit code $LASTEXITCODE" }

  & tar.exe -czf $tasksBundle --exclude=.git --exclude=frontend/node_modules --exclude=frontend/dist --exclude=frontend/dist-guide-test -C $tasksSource .
  if ($LASTEXITCODE -ne 0) { throw "Tasks bundle creation failed with exit code $LASTEXITCODE" }
}

function Invoke-External([string]$Label, [scriptblock]$Command) {
  Write-Host "> $Label" -ForegroundColor Cyan
  if ($DryRun) { return }
  & $Command
  if ($LASTEXITCODE -ne 0) { throw "$Label failed with exit code $LASTEXITCODE" }
}

Require-File $startScript
Require-File $remoteHelper
foreach ($command in 'scp', 'ssh', 'tar.exe') {
  if (-not (Get-Command $command -ErrorAction SilentlyContinue)) { throw "missing command: $command" }
}

Write-Host '> package current Hub and Tasks source bundles' -ForegroundColor Cyan
New-CurrentBundles
Require-File $hubBundle
Require-File $tasksBundle

$ExpectedHubHash = (Get-FileHash -LiteralPath $hubBundle -Algorithm SHA256).Hash
$ExpectedTasksHash = (Get-FileHash -LiteralPath $tasksBundle -Algorithm SHA256).Hash
$hashManifest = Join-Path ([System.IO.Path]::GetTempPath()) 'pj-general-p0-redeploy-hashes.txt'

Write-Host 'pj-general P0 frontend redeploy' -ForegroundColor Yellow
Write-Host "Hub SHA-256:   $ExpectedHubHash"
Write-Host "Tasks SHA-256: $ExpectedTasksHash"
Write-Host 'This script never removes data, volumes, or files; it never imports data or displays environment contents.' -ForegroundColor DarkGray

if ($DryRun) {
  Write-Host "Would upload Hub bundle, Tasks bundle, start script and remote helper to ${remote}:/tmp/"
  Write-Host "Would run the remote helper with its uploaded hash manifest for source-only extraction and ./start-pj-general.sh --start --rebuild-vikunja"
  exit 0
}

@(
  "HUB_EXPECTED=$ExpectedHubHash"
  "TASKS_EXPECTED=$ExpectedTasksHash"
) | Set-Content -LiteralPath $hashManifest -Encoding ascii

try {
  Invoke-External 'upload current bundles and deploy script (SSH password may be requested)' {
    scp -- $hubBundle $tasksBundle $startScript $remoteHelper $hashManifest "${remote}:/tmp/"
  }

  Write-Host '> run safe Linux redeploy (sudo password may be requested)' -ForegroundColor Cyan
  ssh -tt $remote 'bash /tmp/redeploy-p0-frontend-remote.sh'
  if ($LASTEXITCODE -ne 0) { throw "Linux redeploy failed with exit code $LASTEXITCODE" }
} finally {
  Remove-Item -LiteralPath $hashManifest -Force -ErrorAction SilentlyContinue
}

Write-Host 'P0 frontend redeploy succeeded. Open the P0 acceptance HTML and complete the current red/yellow check.' -ForegroundColor Green
