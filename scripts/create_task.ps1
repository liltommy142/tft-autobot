# PowerShell helper to create a scheduled task that runs fetch_from_riot.py daily at 2:30 AM
# Usage (PowerShell elevated):
#   .\create_task.ps1 -Summoner tommy -Platform vn1 -Time "02:30"
param(
    [Parameter(Mandatory=$true)]
    [string] $Summoner,

    [string] $Platform = "vn1",

    [string] $Time = "02:30"
)

$scriptPath = "$PSScriptRoot\fetch_from_riot.py"
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "`"$scriptPath`" $Summoner $Platform"
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
$taskName = "TFT-FetchMeta-$Summoner"
Register-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -TaskName $taskName -Force
Write-Output "Scheduled task '$taskName' created to run daily at $Time."