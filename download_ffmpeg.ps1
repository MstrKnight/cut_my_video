# PowerShell script to download FFmpeg for Cut It Now application

# Define the download URL for FFmpeg (essentials build)
$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$downloadPath = Join-Path $PSScriptRoot "ffmpeg-release-essentials.zip"
$extractPath = Join-Path $PSScriptRoot "ffmpeg-temp"
$assetsFolder = Join-Path $PSScriptRoot "assets"

# Create assets folder if it doesn't exist
if (-not (Test-Path $assetsFolder)) {
    New-Item -Path $assetsFolder -ItemType Directory -Force | Out-Null
    Write-Output "Created assets folder"
}

# Download FFmpeg
Write-Output "Downloading FFmpeg from $ffmpegUrl..."
Invoke-WebRequest -Uri $ffmpegUrl -OutFile $downloadPath
Write-Output "Download completed"

# Extract the ZIP file
Write-Output "Extracting FFmpeg..."
Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force

# Find the ffmpeg.exe file in the extracted content
$ffmpegExe = Get-ChildItem -Path $extractPath -Filter "ffmpeg.exe" -Recurse | Select-Object -First 1

if ($ffmpegExe) {
    # Copy ffmpeg.exe to assets folder
    Copy-Item -Path $ffmpegExe.FullName -Destination (Join-Path $assetsFolder "ffmpeg.exe") -Force
    Write-Output "FFmpeg executable copied to assets folder"
} else {
    Write-Error "Could not find ffmpeg.exe in the extracted files"
}

# Clean up
Write-Output "Cleaning up temporary files..."
Remove-Item -Path $downloadPath -Force
Remove-Item -Path $extractPath -Recurse -Force

Write-Output "FFmpeg setup completed!"
