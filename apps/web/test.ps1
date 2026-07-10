$ErrorActionPreference = "Stop"

$node = & "$PSScriptRoot\find-node.ps1"
& $node --test "$PSScriptRoot\test\api.test.mjs"
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

$python = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (Test-Path -LiteralPath $python) {
  $env:PYTHONPATH = $PSScriptRoot
  $env:PYTHONUTF8 = "1"
  & $python -m unittest discover -s "$PSScriptRoot\test" -p "test_*.py"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
