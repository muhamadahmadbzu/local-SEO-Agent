# Install Local SEO Agent for Claude Code (Windows PowerShell).
#
#   powershell -ExecutionPolicy Bypass -File install.ps1
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Global -Census
#   powershell -ExecutionPolicy Bypass -File install.ps1 -Dir "C:\work\seo"
#
# One-liner (works when the GitHub repo is public):
#   irm https://raw.githubusercontent.com/muhamadahmadbzu/local-SEO-Agent/main/install.ps1 | iex
param(
    [string]$Dir = (Join-Path $HOME "local-SEO-Agent"),
    [string]$Branch = "main",
    [switch]$Global,
    [switch]$Census,
    [switch]$NoClaude
)
# "Continue", not "Stop": Windows PowerShell 5.1 treats any stderr output from native programs (python, git) as a
# terminating error under "Stop", and unittest / git / the Census fetcher all write progress to stderr.
# Failures are detected explicitly through $LASTEXITCODE instead.
$ErrorActionPreference = "Continue"
$RepoUrl = "https://github.com/muhamadahmadbzu/local-SEO-Agent.git"

function Say($m)  { Write-Host "==> $m" -ForegroundColor Green }
function Warn($m) { Write-Host "!!  $m" -ForegroundColor Yellow }
function Die($m)  { Write-Host "xx  $m" -ForegroundColor Red; exit 1 }

# ---------------------------------------------------------------- prerequisites
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Die "git is not installed. Get it from https://git-scm.com/download/win and re-run." }

$Py = $null
foreach ($c in @("python", "py", "python3")) {
    if (Get-Command $c -ErrorAction SilentlyContinue) {
        & $c -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) { $Py = $c; break }
    }
}
if (-not $Py) { Die "Python 3.9+ is required. Install it from https://www.python.org/downloads/ (tick 'Add to PATH') and re-run." }
Say "Python: $(& $Py --version 2>&1)"

if (Get-Command claude -ErrorAction SilentlyContinue) {
    Say "Claude Code found"
} elseif (-not $NoClaude -and (Get-Command npm -ErrorAction SilentlyContinue)) {
    $ans = Read-Host "Claude Code is not installed. Install it now with npm? [y/N]"
    if ($ans -match '^[yY]') { npm install -g @anthropic-ai/claude-code } else { Warn "Skipped. Install later: npm install -g @anthropic-ai/claude-code" }
} else {
    Warn "Claude Code not found. Install it: https://code.claude.com/docs/en/setup"
}

# ---------------------------------------------------------------- get the code
if (Test-Path (Join-Path $Dir ".git")) {
    Say "Updating existing install in $Dir"
    git -C $Dir fetch --quiet origin $Branch 2>$null
    $dirty = git -C $Dir status --porcelain -- . ":!projects"
    if ($dirty) { Warn "Local changes found outside projects/ - skipping update." }
    else {
        git -C $Dir checkout --quiet $Branch 2>$null
        git -C $Dir pull --quiet --ff-only origin $Branch 2>$null
        if ($LASTEXITCODE -ne 0) { Warn "Could not fast-forward; update manually with git pull." }
    }
} elseif (Test-Path $Dir) {
    Die "$Dir exists but is not a git checkout. Use -Dir to pick another folder."
} else {
    Say "Cloning into $Dir"
    git clone --quiet --branch $Branch $RepoUrl $Dir
    if ($LASTEXITCODE -ne 0) { Die "Clone failed. If the repo is private, sign in to GitHub first (gh auth login) and re-run." }
}
Set-Location $Dir

# ---------------------------------------------------------------- verify
$agents = (Get-ChildItem ".claude\agents\*.md").Count
$skills = (Get-ChildItem ".claude\skills" -Directory).Count
Say "Found $agents agents and $skills skills"
Say "Running self-tests..."
& $Py -m unittest discover -s tests > "$env:TEMP\local-seo-agent-tests.log" 2>&1
if ($LASTEXITCODE -eq 0) { Say "Tests passed" } else { Warn "Some tests failed - see $env:TEMP\local-seo-agent-tests.log" }

# ---------------------------------------------------------------- optional: global agents & skills (copies; re-run to update)
if ($Global) {
    $ca = Join-Path $HOME ".claude\agents"; $cs = Join-Path $HOME ".claude\skills"
    New-Item -ItemType Directory -Force -Path $ca, $cs | Out-Null
    $ErrorActionPreference = "Stop"
    Copy-Item ".claude\agents\*.md" $ca -Force
    Get-ChildItem ".claude\skills" -Directory | ForEach-Object {
        Copy-Item $_.FullName (Join-Path $cs $_.Name) -Recurse -Force
    }
    $ErrorActionPreference = "Continue"
    Say "Copied agents and skills into $HOME\.claude (re-run this installer to update them)"
    Warn "The helper scripts live in $Dir - start Claude there for project work."
}

# ---------------------------------------------------------------- optional: Census data
if ($Census) {
    Say "Downloading official Census city data (a few minutes)..."
    & $Py scripts\fetch_census_data.py
    if ($LASTEXITCODE -ne 0) { Warn "Census download failed; the bundled GeoNames city list will be used." }
}

Write-Host ""
Write-Host "Local SEO Agent is installed." -ForegroundColor Green
Write-Host "  cd `"$Dir`""
Write-Host "  claude"
Write-Host ""
Write-Host "Then inside Claude Code:"
Write-Host "  /agents                      -> see the 14-agent team"
Write-Host "  /rank-and-rent discover      -> find niches and cities worth building"
