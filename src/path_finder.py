import os.path
import sys


import logger_conf

logger = logger_conf.Log.logger

class PathFinder:
    @staticmethod
    def get_cache_directory() -> str:
        # Si l'application est en .exe
        if getattr(sys, 'frozen', False):
            logger.info("Twysn is frozen")

            datadir = os.path.dirname(sys.executable) # Répertoire de l'exécutable
            logger.info(datadir)

            chemin_absolu = datadir + "/data/cache"
            logger.info(chemin_absolu)
            logger.info(os.path.abspath(chemin_absolu))
            # print(chemin_absolu)
            return chemin_absolu

        # Si l'application est en développement
        else:
            chemin_relatif = "/../data/cache"
            chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)
            print(chemin_absolu)
            return chemin_absolu
            # logger.info("Twysn isn't frozen, secret file : " + chemin_absolu)

    # TODO Adapter pour Assets
    @staticmethod
    def getAssetsDirectory() -> str:
        if getattr(sys, 'frozen', False):
            # L'application est en .exe
            datadir = os.path.dirname(sys.executable)
            chemin_relatif = "secrets"
            chemin_absolu = os.path.abspath(os.path.dirname(sys.executable) + "/" + chemin_relatif)
            # logger.info("Twysn is frozen, secret file : " + chemin_absolu)

        else:
            # L'application est en dev
            chemin_relatif = "/../data/secrets"
            chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)
            # logger.info("Twysn isn't frozen, secret file : " + chemin_absolu)

    # TODO Adapter pour Data
    @staticmethod
    def getDataDirectory() -> str:
        if getattr(sys, 'frozen', False):
            # L'application est en .exe
            datadir = os.path.dirname(sys.executable)
            chemin_relatif = "secrets"
            chemin_absolu = os.path.abspath(os.path.dirname(sys.executable) + "/" + chemin_relatif)
            # logger.info("Twysn is frozen, secret file : " + chemin_absolu)

        else:
            # L'application est en dev
            chemin_relatif = "/../data/secrets"
            chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)
            # logger.info("Twysn isn't frozen, secret file : " + chemin_absolu)
