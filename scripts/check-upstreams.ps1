$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$stateDir = Join-Path $root ".chip-design"
$stateFile = Join-Path $stateDir "upstream-check.json"
$today = Get-Date -Format "yyyy-MM-dd"

New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

if (Test-Path $stateFile) {
    try {
        $state = Get-Content -Raw -Path $stateFile | ConvertFrom-Json
        if ($state.last_checked -eq $today) {
            Write-Output "chip-design upstream check skipped: already checked $today"
            exit 0
        }
    } catch {
        Write-Output "chip-design upstream check state unreadable; refreshing"
    }
}

$submodules = @(
    "upstreams/design-taste-frontend",
    "upstreams/gpt-taste"
)

$results = @()

foreach ($submodule in $submodules) {
    $path = Join-Path $root $submodule
    if (-not (Test-Path $path)) {
        $results += [PSCustomObject]@{
            submodule = $submodule
            status = "missing"
            current = $null
            remote = $null
        }
        continue
    }

    Push-Location $path
    try {
        $current = git rev-parse HEAD
        git fetch --quiet origin
        $branch = git rev-parse --abbrev-ref HEAD
        $remote = git rev-parse "origin/$branch"
        $status = if ($current -eq $remote) { "up-to-date" } else { "update-available" }

        $results += [PSCustomObject]@{
            submodule = $submodule
            status = $status
            current = $current
            remote = $remote
        }
    } finally {
        Pop-Location
    }
}

$payload = [PSCustomObject]@{
    last_checked = $today
    checked_at = (Get-Date).ToString("o")
    results = $results
}

$payload | ConvertTo-Json -Depth 5 | Set-Content -Path $stateFile -Encoding utf8

foreach ($result in $results) {
    Write-Output ("{0}: {1}" -f $result.submodule, $result.status)
}

if ($results.status -contains "update-available") {
    exit 2
}

if ($results.status -contains "missing") {
    exit 1
}
