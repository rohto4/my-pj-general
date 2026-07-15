[CmdletBinding()]
param(
  [string]$VaultRoot = 'G:\knowledge-vault',
  [string]$Server = '192.168.0.200',
  [string]$User = 'unibell4',
  [string]$IdentityFile = (Join-Path $env:USERPROFILE '.ssh\codex_pjserver_ed25519'),
  [string]$LlmBaseUrl = '',
  [string]$LlmModel = 'local-unverified',
  [string]$AllowedTags = '',
  [int]$Limit = 30,
  [switch]$NoLlm,
  [switch]$RequireLlm,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$collector = Join-Path $repoRoot 'apps\web\vault_intake.py'
$remoteHelper = Join-Path $PSScriptRoot 'import-knowledge-vault-remote.sh'
$batch = Join-Path $repoRoot 'tmp\threadline-knowledge-vault-batch.json'
$manifest = Join-Path $repoRoot 'tmp\threadline-knowledge-vault-manifest.json'
$remote = "$User@$Server"
$sshOptions = @('-i', $IdentityFile, '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes')

function Require-File([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "missing required file: $Path" }
}

function Resolve-Python {
  $command = Get-Command python -ErrorAction SilentlyContinue
  if ($command) { return $command.Source }
  $bundled = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
  if (Test-Path -LiteralPath $bundled -PathType Leaf) { return $bundled }
  throw 'Python runtime was not found'
}

Require-File $collector
Require-File $remoteHelper
if (-not (Test-Path -LiteralPath $VaultRoot -PathType Container)) { throw "missing Vault root: $VaultRoot" }
$python = Resolve-Python
if (-not $AllowedTags) {
  try {
    $bootstrap = Invoke-RestMethod -Uri "http://${Server}:4173/api/bootstrap" -TimeoutSec 5
    $AllowedTags = (($bootstrap.tags | Where-Object { $_.visible } | ForEach-Object { $_.name }) -join ',')
  } catch {
    Write-Warning 'Hub tag master could not be read; AI tag suggestions are disabled for this batch.'
  }
}
$collectArgs = @(
  $collector, 'collect-vault-batch', '--root', $VaultRoot,
  '--output', $batch, '--manifest', $manifest, '--limit', [string]$Limit,
  '--llm-model', $LlmModel
)
if ($AllowedTags) { $collectArgs += @('--allowed-tags', $AllowedTags) }
if ($NoLlm) {
  $collectArgs += '--no-llm'
} elseif ($LlmBaseUrl) {
  $collectArgs += @('--llm-base-url', $LlmBaseUrl)
}
if ($RequireLlm) { $collectArgs += '--require-llm' }

Write-Host '> collect knowledge-vault into an evidence-checked batch' -ForegroundColor Cyan
& $python @collectArgs
if ($LASTEXITCODE -ne 0) { throw "collect-vault-batch failed with exit code $LASTEXITCODE" }
Require-File $batch
Require-File $manifest
$hash = (Get-FileHash -LiteralPath $batch -Algorithm SHA256).Hash.ToLowerInvariant()
$manifestData = Get-Content -Raw -Encoding UTF8 $manifest | ConvertFrom-Json
if ($hash -ne [string]$manifestData.sha256) { throw 'local batch hash does not match manifest' }

Write-Host "Batch: $($manifestData.batch_id)"
Write-Host "SHA-256: $hash"
Write-Host 'The Vault is read-only; SQLite files, secrets and environment contents are never transferred.' -ForegroundColor DarkGray

if ($DryRun) {
  Write-Host 'Dry run complete. Batch and manifest were created; no SSH transfer or Linux write was performed.' -ForegroundColor Yellow
  exit 0
}

Require-File $IdentityFile
foreach ($command in 'scp', 'ssh') {
  if (-not (Get-Command $command -ErrorAction SilentlyContinue)) { throw "missing command: $command" }
}

Write-Host '> upload batch, manifest and fixed remote importer' -ForegroundColor Cyan
scp @sshOptions -- $batch $manifest $remoteHelper "${remote}:/tmp/"
if ($LASTEXITCODE -ne 0) { throw "SCP failed with exit code $LASTEXITCODE" }

Write-Host '> verify SHA-256 and import through the Hub DB boundary' -ForegroundColor Cyan
ssh @sshOptions $remote 'bash /tmp/import-knowledge-vault-remote.sh /tmp/threadline-knowledge-vault-batch.json /tmp/threadline-knowledge-vault-manifest.json'
if ($LASTEXITCODE -ne 0) { throw "Linux batch import failed with exit code $LASTEXITCODE" }

Write-Host 'knowledge-vault batch import succeeded. Review pending candidates in Thread Line Hub; no GO was performed.' -ForegroundColor Green
