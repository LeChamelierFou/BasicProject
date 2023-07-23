##### Lier le bot à une clé API #####

1. Accéder à la page : https://www.bybit.com/app/user/api-management
    1.a Si non existante, cliquez sur le boutonj "Create an API Key" sur le lien suivant :
        https://www.bybit.com/future-activity/en-US/developer
2. Connecter vous à votre compte bybit
3. Cliquer sur Create New Key, puis sur System-generated API keys
4. Dans API Key Usage :
    4.a Conserver le champ "API Transaction"
    4.b Donner un nom à cette clé API selon votre besoin dans le champ "Name for the API key"
5. Dans API Key Permissions
    5.a Sélectionner "Read-Write"
    5.b Sélectionner "Only IPs with permissions granted are allowed to access the OpenAPI"
    5.c Renseigner vos adresses IP connues pour éviter des utilisations par des utilisateurs tierces.
        Ne pas oublier d'ajouter les nouvelles si jamais vous souhaitez vous en servir ailleurs que chez vous
    5.d Sélectionner le bouton "Standard Account" qui sélectionnera les champs pour Contract, USDC Contracts et SPOT
6. Appuyer sur le bouton Submit
7. Conserver vos clés API bien à l'abri
8. Insérer ces clés API dans le fichier de configuration : "config.ini"

##### Faire fonctionner le bot sur docker #####

1. Installer docker
2. En parallèle, lancer powershell en mode administrateur
3. Exécuter la commande : Set-ExecutionPolicy RemoteSigned
4. Valider la modification de stratégie en saisissant : "O"
5. Quand Docker est installé lancer le script InstallDockerContainer.ps1 avec powershell
    5.a : Si une erreur apparait, contacter votre service technique
6. Pour lancer le bot, lancer le script ExecuteDockerContainer.ps1 avec powershell
7. Pour couper le bot, lancer le script StopDockerContainer.ps1 avec powershell
8. TO-DO : Faire un script de récupération des trades effectués par le bot pour les analyser