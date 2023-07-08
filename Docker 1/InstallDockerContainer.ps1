docker build -t optimumtrade .
docker run -d -p 2368:2368 --name optimumtrade optimumtrade
$containerId = docker ps -aqf name=optimumtrade
docker stop $containerId
Read-Host -Prompt "Press any key to continue..."