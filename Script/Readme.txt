1. Installer docker
2. En parallèle, lancer powershell en mode administrateur
3. Exécuter la commande : Set-ExecutionPolicy RemoteSigned
4. Valider la modification de stratégie en saisissant : "O"
5. Quand Docker est installé lancer le script InstallDockerContainer.ps1 avec powershell
    5.a : Si une erreur apparait, contacter votre service technique
6. Pour lancer le bot, lancer le script ExecuteDockerContainer.ps1 avec powershell
7. Pour couper le bot, lancer le script StopDockerContainer.ps1 avec powershell
8. TO-DO : Faire un script de récupération des trades effectués par le bot pour les analyser