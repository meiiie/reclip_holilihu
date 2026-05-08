param(
    [Parameter(Mandatory = $true)]
    [string]$RepoUrl,

    [string]$InstallDir = "$env:LOCALAPPDATA\HoLiLiHu-ReClip-src",

    [string]$Branch = "main",

    [switch]$SkipCodexConfig
)

$ErrorActionPreference = "Stop"

function Write-Step($Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function ConvertTo-TomlString($Value) {
    return '"' + ($Value -replace '\\', '\\' -replace '"', '\"') + '"'
}

function Get-PythonLauncher {
    $commands = @("py", "python")
    foreach ($command in $commands) {
        $found = Get-Command $command -ErrorAction SilentlyContinue
        if ($found) {
            return $command
        }
    }
    throw "Python 3.10+ was not found. Install Python first, then rerun this script."
}

Write-Step "Preparing install directory"
$parent = Split-Path -Parent $InstallDir
if ($parent) {
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
}

if (Test-Path (Join-Path $InstallDir ".git")) {
    Write-Step "Updating existing clone"
    git -C $InstallDir fetch origin $Branch
    git -C $InstallDir checkout $Branch
    git -C $InstallDir pull --ff-only origin $Branch
} else {
    if (Test-Path $InstallDir) {
        throw "InstallDir exists but is not a Git repo: $InstallDir"
    }
    Write-Step "Cloning repository"
    git clone --branch $Branch --depth 1 $RepoUrl $InstallDir
}

Write-Step "Creating Python virtual environment"
$pythonLauncher = Get-PythonLauncher
if ($pythonLauncher -eq "py") {
    py -3.10 -m venv (Join-Path $InstallDir ".venv")
    if ($LASTEXITCODE -ne 0) {
        py -3 -m venv (Join-Path $InstallDir ".venv")
    }
} else {
    python -m venv (Join-Path $InstallDir ".venv")
}

$venvPython = Join-Path $InstallDir ".venv\Scripts\python.exe"
if (!(Test-Path $venvPython)) {
    throw "Virtual environment was not created correctly: $venvPython"
}

Write-Step "Installing Python dependencies"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $InstallDir "requirements.txt")

if (!$SkipCodexConfig) {
    Write-Step "Configuring Codex MCP"
    $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
    New-Item -ItemType Directory -Force -Path $codexHome | Out-Null
    $configPath = Join-Path $codexHome "config.toml"
    $serverPath = Join-Path $InstallDir "mcp_server.py"

    $block = @"
[mcp_servers.holilihu-reclip]
command = $(ConvertTo-TomlString $venvPython)
args = [$(ConvertTo-TomlString $serverPath)]
cwd = $(ConvertTo-TomlString $InstallDir)
startup_timeout_sec = 20
tool_timeout_sec = 7200
"@

    $content = ""
    if (Test-Path $configPath) {
        $content = Get-Content -Raw -Path $configPath
        $pattern = "(?ms)^\[mcp_servers\.holilihu-reclip\]\r?\n.*?(?=^\[|\z)"
        $content = [regex]::Replace($content, $pattern, "").TrimEnd()
    }

    if ($content.Length -gt 0) {
        $content = $content + "`r`n`r`n" + $block + "`r`n"
    } else {
        $content = $block + "`r`n"
    }
    Set-Content -Path $configPath -Value $content -Encoding UTF8
    Write-Host "Configured: $configPath" -ForegroundColor Green
}

Write-Step "Done"
Write-Host "Repository: $InstallDir"
Write-Host "Run app:    $venvPython app.py"
Write-Host "MCP file:   $(Join-Path $InstallDir 'mcp_server.py')"
Write-Host ""
Write-Host "Restart Codex so it reloads MCP configuration." -ForegroundColor Yellow
