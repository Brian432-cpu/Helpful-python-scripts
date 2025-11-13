# --------------------------------------------
# Windows Performance Optimization Script
# Author: Brian's AI Assistant 😊
# --------------------------------------------

Write-Host "Starting Windows Optimization..." -ForegroundColor Cyan

# 1️⃣ Clean temporary files and Windows cache
Write-Host "Cleaning temporary files..."
Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Temporary files cleaned." -ForegroundColor Green

# 2️⃣ Clear Windows Update cache
Write-Host "Clearing Windows Update cache..."
net stop wuauserv
Remove-Item "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
net start wuauserv
Write-Host "Windows Update cache cleared." -ForegroundColor Green

# 3️⃣ Disable unnecessary startup programs
Write-Host "Disabling unnecessary startup apps..."
Get-CimInstance Win32_StartupCommand | 
    Where-Object { $_.Command -notmatch "Windows Defender|OneDrive|SecurityHealth" } | 
    ForEach-Object { 
        Write-Host "Disabling: $($_.Name)"
        Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name $_.Name -ErrorAction SilentlyContinue
    }
Write-Host "Startup apps optimized." -ForegroundColor Green

# 4️⃣ Optimize memory and pagefile settings
Write-Host "Optimizing memory and pagefile settings..."
wmic computersystem where name="%computername%" set AutomaticManagedPagefile=True
Write-Host "Memory optimized." -ForegroundColor Green

# 5️⃣ Defragment hard drives (skip if SSD)
Write-Host "Defragmenting HDD (if applicable)..."
defrag C: /O
Write-Host "Disk optimized." -ForegroundColor Green

# 6️⃣ Stop unnecessary background services
Write-Host "Stopping unnecessary background services..."
$services = @(
    "SysMain", # Superfetch
    "DiagTrack", # Connected User Experiences
    "Fax",
    "MapsBroker",
    "RemoteRegistry"
)

foreach ($s in $services) {
    Stop-Service -Name $s -ErrorAction SilentlyContinue
    Set-Service -Name $s -StartupType Disabled -ErrorAction SilentlyContinue
    Write-Host "Stopped and disabled service: $s"
}

# 7️⃣ Clear DNS cache
Write-Host "Flushing DNS cache..."
ipconfig /flushdns

# 8️⃣ Final message
Write-Host "`n✅ Optimization complete! Please restart your PC for best performance." -ForegroundColor Cyan
