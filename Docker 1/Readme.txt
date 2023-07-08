1. Installer docker
2. Lancer un invité de commande / terminal dans le dossier de docker
3. Exécuter la commande : docker build -t optimumtrade .
4. Exécuter la commande : docker run -d optimumtrade
5. Exécuter la commande : docker ps
6. Récupérer le container_ID lié à l'image optimum trade
7. Exécuter la commande : docker exec Container_ID bash
8. Une fois dans le bash linux, lancer la commande : python ./BotInfrastructure.python
9. Pour l'arrêter, faites ctrl + c
10. Pour quitter le docker taper exit
11. Pour stopper le docker, taper docker stop Container_ID