# Move up 1 directory level
Set-Location (Get-Location | Split-Path)

# Check if folder exist, delete if yes
if (Test-Path -Path "__pycache__") {
    Remove-Item "__pycache__" -Recurse
}
if (Test-Path -Path "app_data") {
    Remove-Item "app_data" -Recurse
}
if (Test-Path -Path "data") {
    Remove-Item "data" -Recurse
}

# Check if file exist, delete if yes
if (Test-Path "*.ini") {
    Remove-Item "*.ini"
}

Read-Host "Completed!`nPress any key to continue..."