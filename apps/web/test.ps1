$ErrorActionPreference = "Stop"

$node = & "$PSScriptRoot\find-node.ps1"
& $node --test "$PSScriptRoot\test\api.test.mjs"
