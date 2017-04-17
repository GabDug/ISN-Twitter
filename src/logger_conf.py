import logging
from sys import stdout

class Log():
    # On crée un logger : c'est pour gérer les logs de l'application
    # Je vais essayer de remplacer tous les logger.debug() par des logger.info() ou logger.warning() etc
    # Ca permet plus de clarté (ce qui est normal ou pas...) et de mettre dans un fichier
    # Ca permet aussi d'avoir le moment précis de tel ou tel message pour savoir où on en est dans le code (pratique!)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(stdout)
    ch.setLevel(logging.DEBUG)

    f = logging.FileHandler("twisn.log", mode="w")
    f.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(funcName)s in %(filename)s] : %(message)s")
    formatter.datefmt = "%H:%M:%S"
    ch.setFormatter(formatter)
    f.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(f)

    logger.info("Starting logger")