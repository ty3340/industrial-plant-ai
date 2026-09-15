<#
  docker-run.ps1 - build & run the batch-plant Docker stack.

  WHY THIS EXISTS: this project lives on your Desktop, which Windows 11 keeps
  inside OneDrive. Docker cannot build from a OneDrive-synced folder - its
  cloud-placeholder files break the build ("archive/tar: unknown file mode").
  This script keeps your project on the Desktop (edit here as normal) and builds
  from an automatic local copy at C:\dev, so you never have to move anything.

  USAGE (from a PowerShell terminal in this folder):
      .\docker-run.ps1
  If Windows blocks the script:
      powershell -ExecutionPolicy Bypass -File .\docker-run.ps1

  Stop the stack later with:
      docker compose -f "C:\dev\Industrial-AI-Project\docker-compose.yml" down
#>
$ErrorActionPreference = "Stop"

$src   = $PSScriptRoot                       # the Desktop project (where this file lives)
$build = "C:\dev\Industrial-AI-Project"      # throwaway local build copy (not in OneDrive)

# 1. Make sure the Docker engine is running (start Docker Desktop if needed).
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker engine not running - starting Docker Desktop..." -ForegroundColor Cyan
    $exe = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $exe) { Start-Process $exe }
    for ($i = 0; $i -lt 40; $i++) { Start-Sleep 5; docker info *> $null; if ($LASTEXITCODE -eq 0) { break } }
    if ($LASTEXITCODE -ne 0) { throw "Docker did not start. Open Docker Desktop manually, then re-run." }
}

# 2. Sync this project to the local build folder (excludes env/deps that Docker rebuilds).
Write-Host "Syncing project -> $build ..." -ForegroundColor Cyan
robocopy $src $build /MIR /XD "$src\.venv" "$src\.git" node_modules __pycache__ .pytest_cache /XF *.pyc | Out-Null

# 3. Build and start the stack from the local copy.
Write-Host "Building and starting containers (first build takes a few minutes)..." -ForegroundColor Cyan
Push-Location $build
try { docker compose up -d --build } finally { Pop-Location }

Write-Host "`nStack is up:" -ForegroundColor Green
Write-Host "  App : http://localhost:5173"
Write-Host "  API : http://localhost:8001/health/deep"
Write-Host "`nStop it with:  docker compose -f `"$build\docker-compose.yml`" down"
