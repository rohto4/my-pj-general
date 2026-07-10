$ErrorActionPreference = "Stop"

$command = Get-Command node -ErrorAction SilentlyContinue
if ($command) {
  Write-Output $command.Source
  exit 0
}

$codexNode = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
if (Test-Path -LiteralPath $codexNode) {
  Write-Output $codexNode
  exit 0
}

throw "Node.js was not found in PATH and Codex bundled Node.js was not found."
