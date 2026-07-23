# Refresh PATH so npm/node are found even in sessions opened before Node was installed
$env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path', 'User')

Set-Location "$PSScriptRoot\frontend"
npm run dev
