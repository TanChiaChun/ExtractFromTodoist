# Move up 1 directory level
Set-Location (Get-Location | Split-Path)

function My-Clear-Folder {
    # Check if folder exist, delete if yes
    if (Test-Path -Path "__pycache__") {
        Remove-Item "__pycache__" -Recurse
    }
    if (Test-Path -Path "pyinstaller\build") {
        Remove-Item "pyinstaller\build" -Recurse
    }
    if (Test-Path -Path "pyinstaller\dist") {
        Remove-Item "pyinstaller\dist" -Recurse
    }

    # Check if file exist, delete if yes
    if (Test-Path "pyinstaller\*.spec") {
        Remove-Item "pyinstaller\*.spec"
    }
}

# Run My-Clear-Folder function
My-Clear-Folder

# Check if file exist, delete if yes
if (Test-Path "pyinstaller\*.exe") {
    Remove-Item "pyinstaller\*.exe"
}

# Set project name
$proj_name = Split-Path (Get-Location) -Leaf
$script_name = "$proj_name.py"
if (-not (Test-Path $script_name) ) {
    $proj_name = Read-Host "Input project name"
    $script_name = "$proj_name.py"
}
$proj_version = Read-Host "Input project version"
$exe_name = "$proj_name" + "_v" + "$proj_version.exe"

# Check if folder exist, create if no
if (-not (Test-Path -Path "pyinstaller") ) {
    New-Item -Name "pyinstaller" -ItemType "directory"
}

# Check if file exist, create if no
if (-not (Test-Path "pyinstaller\python-icon.ico") ) {
    $ico_source = Get-Location | Split-Path
    if (-not (Test-Path -Path "$ico_source\python-icon.ico") ) {
        $ico_source = Read-Host "Input source folder for ico file"
    }
    Copy-Item "$ico_source\python-icon.ico" -Destination "pyinstaller"
}

# Run Pyinstaller
venv\Scripts\Activate.ps1
pyinstaller $script_name --onefile --icon python-icon.ico --distpath ./pyinstaller/dist --workpath ./pyinstaller/build --specpath ./pyinstaller
Move-Item -Path "pyinstaller\dist\$proj_name.exe" -Destination "pyinstaller\$exe_name"
My-Clear-Folder

Read-Host "Completed!`nPress any key to continue..."