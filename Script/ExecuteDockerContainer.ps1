docker start optimumtrade
$containerId = docker ps -aqf name=optimumtrade
docker exec $containerId bash