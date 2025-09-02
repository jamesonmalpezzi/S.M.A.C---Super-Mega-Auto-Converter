# PowerShell script to build transcode_gui.py into a standalone executable using PyInstaller and start it

# Ensure PyInstaller is installed
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "PyInstaller not found. Installing PyInstaller..."
    pip install pyinstaller
}

# Define paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir "transcode_gui.py"
$handbrakeCli = "C:\Program Files\HandBrake\HandBrakeCLI.exe"
$outputDir = $scriptDir
$executable = Join-Path $outputDir "SMAC.exe"

# Verify that transcode_gui.py exists
if (-not (Test-Path $pythonScript)) {
    Write-Host "Error: transcode_gui.py not found in $scriptDir"
    exit 1
}

# Stop any running SMAC.exe processes to avoid permission issues
Write-Host "Checking for running SMAC.exe processes..."
Stop-Process -Name "SMAC" -Force -ErrorAction SilentlyContinue

# Remove existing executable with retry mechanism
if (Test-Path $executable) {
    Write-Host "Removing existing $executable..."
    $retryCount = 0
    $maxRetries = 3
    while ($retryCount -lt $maxRetries) {
        try {
            Remove-Item -Path $executable -Force -ErrorAction Stop
            Write-Host "Successfully removed $executable"
            break
        }
        catch {
            $retryCount++
            Write-Host "Attempt $retryCount failed to remove $executable : $_"
            Start-Sleep -Seconds 2
            if ($retryCount -eq $maxRetries) {
                Write-Host "Error: Failed to remove $executable after $maxRetries attempts"
                exit 1
            }
        }
    }
}

# Prepare PyInstaller command
$pyinstallerArgs = @(
    "--onefile",
    "--windowed",
    "--name=SMAC",
    "--distpath", $outputDir,
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