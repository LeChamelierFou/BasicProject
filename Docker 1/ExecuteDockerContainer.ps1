docker start optimumtrade
$containerId = docker ps -aqf name=optimumtrade
docker exec $containerId bash
python ./BotInfrastructure.py
Read-Host -Prompt "Press any key to continue..."