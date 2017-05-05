import logging
from sys import stdout


class Log:
    # On crée un logger : c'est pour gérer les logs de l'application
    # On peux utiliser logger.debug(), logger.info(), logger.warning(), logger.error()
    # Permet la mise en page des logs, leur lecture sur un fichier même sans console (en .exe)

    # On crée le logger
    logger = logging.getLogger(__name__)
    # On définit quel niveau de log créer (si on met INFO ça ignore les debug)
    logger.setLevel(logging.DEBUG)

    # On crée un "handler" qui va gérer afficher dans la console si elle existe
    # Le handler traite les données du logger
    ch = logging.StreamHandler(stdout)
    ch.setLevel(logging.DEBUG)

    # On crée un "handler" qui va écrire dans un fichier les logs, réécrit à chaque lancement
    f = logging.FileHandler("twisn.log", mode="w")
    f.setLevel(logging.DEBUG)

    # On définit le format des messages : HEURE [NIVEAU] [fonction in fichier] : message
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(funcName)s in %(filename)s] : %(message)s")
    formatter.datefmt = "%H:%M:%S"

    # On définit ce format pour les 2 handlers
    ch.setFormatter(formatter)
    f.setFormatter(formatter)

    # On ajouter les handlers au logger
    logger.addHandler(ch)
    logger.addHandler(f)

    logger.info("Starting logger")
