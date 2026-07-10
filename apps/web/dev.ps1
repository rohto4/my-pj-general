$ErrorActionPreference = "Stop"

$node = & "$PSScriptRoot\find-node.ps1"
& $node "$PSScriptRoot\server.mjs"
