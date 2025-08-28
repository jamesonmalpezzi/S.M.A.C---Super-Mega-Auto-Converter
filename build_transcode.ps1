# PowerShell script to build transcode_gui.py into a standalone executable using PyInstaller and start it

# Ensure PyInstaller is installed
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "PyInstaller not found. Installing PyInstaller..."
    pip install pyinstaller
}

# Define paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir "transcode_gui.py"
$marioImage = Join-Path $scriptDir "images/mario.png"
$handbrakeCli = "C:\Program Files\HandBrake\HandBrakeCLI.exe"
$startSound = Join-Path $scriptDir "sounds/luigi-here-we-go.mp3"
$finishSound = Join-Path $scriptDir "sounds/jobs_done.mp3"
$errorSound = Join-Path $scriptDir "sounds/bmw-bong.mp3"
$outputDir = $scriptDir
$executable = Join-Path $outputDir "SMAC.exe"

# Verify that transcode_gui.py exists
if (-not (Test-Path $pythonScript)) {
    Write-Host "Error: transcode_gui.py not found in $scriptDir"
    exit 1
}

# Verify that mario.png exists
if (-not (Test-Path $marioImage)) {
    Write-Host "Error: images/mario.png not found in $scriptDir"
    exit 1
}

# Verify that sound files exist
$soundFiles = @($startSound, $finishSound, $errorSound)
foreach ($sound in $soundFiles) {
    if (-not (Test-Path $sound)) {
        Write-Host "Error: Sound file $sound not found"
        exit 1
    }
}

# Remove existing executable to avoid permission issues
if (Test-Path $executable) {
    Write-Host "Removing existing $executable..."
    Remove-Item -Path $executable -Force -ErrorAction SilentlyContinue
}

# Prepare PyInstaller command
$pyinstallerArgs = @(
    "--onefile",
    "--windowed",
    "--name=SMAC",
    "--add-data", "${marioImage};images",
    "--add-data", "${startSound};sounds",
    "--add-data", "${finishSound};sounds",
    "--add-data", "${errorSound};sounds",
    "--distpath", $scriptDir,
    "--clean"
)

# Add HandBrakeCLI.exe to the build if it exists
if (Test-Path $handbrakeCli) {
    $pyinstallerArgs += @("--add-binary", "${handbrakeCli};.")
}
else {
    Write-Host "Warning: HandBrakeCLI.exe not found at $handbrakeCli. Ensure it is installed at C:\Program Files\HandBrake\HandBrakeCLI.exe for the executable to function."
}

# Add the Python script
$pyinstallerArgs += $pythonScript

# Run PyInstaller
Write-Host "Building SMAC executable..."
pyinstaller @pyinstallerArgs

# Check if build was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful! Executable is located at $executable"
    
    # Start the executable
    if (Test-Path $executable) {
        Write-Host "Starting SMAC.exe..."
        Start-Process -FilePath $executable
    }
    else {
        Write-Host "Error: Executable $executable not found after build"
        exit 1
    }
}
else {
    Write-Host "Error: Build failed. Check PyInstaller logs for details."
    exit 1
}

# Clean up temporary build files
Write-Host "Cleaning up temporary build files..."
Remove-Item -Path (Join-Path $scriptDir "build") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $scriptDir "SMAC.spec") -Force -ErrorAction SilentlyContinue
Write-Host "Done!"