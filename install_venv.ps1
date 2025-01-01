# Define default directory
$currentDir = "$env:HOMEDRIVE$env:HOMEPATH"

Write-Host "This script will create a Python virtual environment and install required packages."
Write-Host "Python venv environment needs 7 ~ 8 Gigabytes."
Write-Host "Default installation directory is $currentDir, $currentDir\venv will be used."

# Prompt user for installation directory
$installationDir = Read-Host "Enter new directory or press Enter key"
if ([string]::IsNullOrWhiteSpace($installationDir)) {
    $installationDir = $currentDir
}

Write-Host "$installationDir\venv will be used."
Pause

# Check if venv folder exists, if not, create it
if (-Not (Test-Path "$installationDir\venv\Scripts")) {
    Write-Host "Creating venv..."
    python -m venv "$installationDir\venv"
}

# Activate the virtual environment
& "$installationDir\venv\Scripts\activate.ps1"

Write-Host "Python packages will be installed. Ctrl + C to cancel."
Pause

# Install requirements
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "\nRequirements installation failed. Please remove the venv folder and run install_venv.ps1 again."
} else {
    Write-Host "\nRequirements are installed successfully."
}
Pause
