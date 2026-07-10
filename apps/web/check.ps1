$ErrorActionPreference = "Stop"

$node = & "$PSScriptRoot\find-node.ps1"
& $node --check "$PSScriptRoot\app.js"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $node --check "$PSScriptRoot\server.mjs"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$python = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (Test-Path -LiteralPath $python) {
  $env:PYTHONUTF8 = "1"
  $env:PYTHONIOENCODING = "utf-8"
  & $python "$PSScriptRoot\db_tool.py" bootstrap | Out-Null
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
