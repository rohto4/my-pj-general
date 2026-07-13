param(
  [string]$BackupDir = ""
)

$ErrorActionPreference = "Stop"

$python = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
  $pythonCommand = Get-Command python -ErrorAction Stop
  $python = $pythonCommand.Source
}

if ($BackupDir) {
  $env:P0_BACKUP_DIR = [IO.Path]::GetFullPath($BackupDir)
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
"{}" | & $python "$PSScriptRoot\db_tool.py" backup-database
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
