$containerId = docker ps -aqf name=optimumtrade
docker cp ${containerId}:./Output/ResultTrades*.csv ../Output/
docker stop $containerId
Read-Host -Prompt "Press any key to continue..."