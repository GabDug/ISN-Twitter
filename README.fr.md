# Twysn : Projet ISN Twitter
Petit projet créé au lycée pour le bac ISN.

Nous avons utilisé :
- Python 3.6.1
- Tkinter (et ttk)
- Twython: [Doc](https://twython.readthedocs.io), [Github](https://github.com/ryanmcgrath/twython)
- Mttkinter 

Plateformes supportées :
- Windows 10 
- Windows 7+ (problèmes d'affichage majeurs)

## Style
Pour Windows 10, nous nous sommes inspirées du styles des applications UWP.
Voici de la documentation fournie par Microsoft :
- https://developer.microsoft.com/en-us/windows/apps/design
- https://docs.microsoft.com/en-us/windows/uwp/layout/
- PDF http://download.microsoft.com/download/2/4/A/24A81A29-77CF-4AA5-967E-64E42554F21B/UWP%20app%20design%20guidelines%20v1509.pdf
    - Guide pour les polices d'écriture page 302
    - Guide pour faire un formulaire page 305
    
# Organisation des répertoires
- `src` contient le code source de l'application
  - `src/lib` contient le code sources des librairies utilisées qui ne sont pas disponibles via pip
- `assets` contient les ressources à distribuer avec l'applications (jetons de l'application, icones...)
- `data` contient les ressources créées ou téléchargées par le client (Ex: jetons en base 64 de l'utilisateur). Le dossier n'est pas distribué ou est distribué vide avec le client.
  - `data/cache` contient toutes les images téléchargées et en cache. Le cache peut être supprimé manuellement ou via la fenêtre des paramètres.
- `dev_assets` contient des ressources utiles au développement de Twysn, comme des listes de tweets ou des exmples d'utilisateurs.

## Installation
Récupérez les tokens de votre application via le site dédié aux développeurs de Twitter.
Ajoutez les dans le fichier `assets/app_tokens` encodés en base 64, comme expliqué dans `assets/app_tokens_example`.

## License (en)
- Twysn is distributed under the GNU AGPL license. Please see LICENSE.md. 
- mttkinter is distributed under the GNU LGPL license.
- TWITTER, TWEET, RETWEET and the Twitter logo are trademarks of Twitter, Inc. or its affiliates.
