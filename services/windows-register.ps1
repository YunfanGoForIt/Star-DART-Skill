$TaskName = "StarDARTGitHubStarPoller"
$RepoRoot = "C:\Path\star-dart"
$PythonExe = "C:\Python39\python.exe"
$ScriptPath = "$RepoRoot\scripts\webhook_poller.py"

$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory $RepoRoot
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Principal = New-ScheduledTaskPrincipal -UserId $env:UserName -LogonType Interactive -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force
Write-Host "Task registered: $TaskName"
