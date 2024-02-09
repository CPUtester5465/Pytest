$folderPath = "C:\test\test1" 
$limitDate = (Get-Date).AddDays(-31)
$throttleLimit = 10 
$logPath = "C:\file.log" 


$startTime = Get-Date


$filesToDelete = Get-ChildItem -Path $folderPath -File | Where-Object { $_.LastWriteTime -lt $limitDate }


$fileCount = $filesToDelete.Count


$filesToDelete | ForEach-Object -Parallel {
    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
} -ThrottleLimit $throttleLimit


$endTime = Get-Date
$duration = $endTime - $startTime


$logMessage = "Date: $($endTime.ToString('yyyy-MM-dd HH:mm:ss')), Deleted Files: $fileCount, Duration: $($duration.ToString())"
Add-Content -Path $logPath -Value $logMessage

# Output summary
Write-Output $logMessage
