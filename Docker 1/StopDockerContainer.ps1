$containerId = docker ps -aqf name=optimumtrade
docker stop $containerId
Read-Host -Prompt "Press any key to continue..."