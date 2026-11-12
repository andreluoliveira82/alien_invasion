$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$archive = Join-Path $projectRoot "dist\AlienInvasion-win64.zip"

Push-Location $projectRoot
try {
    uv run pyinstaller --clean --noconfirm alien-invasion.spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }
    if (Test-Path -LiteralPath $archive) {
        Remove-Item -LiteralPath $archive
    }
    Compress-Archive -Path "dist\AlienInvasion\*" -DestinationPath $archive
} finally {
    Pop-Location
}
