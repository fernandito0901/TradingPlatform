# Fail fast if Docker Desktop engine is down
$ping = docker info 2>$null
if (!$?) {
    Write-Host "Docker daemon not running. Try:"
    Write-Host "  Start-Menu -> Docker Desktop"
    Write-Host "  OR  cd 'C:\\Program Files\\Docker\\Docker'; ./DockerCli.exe -SwitchDaemon"
    Exit 1
}
