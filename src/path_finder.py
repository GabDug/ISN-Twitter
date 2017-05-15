import os.path
import sys

import logger_conf

logger = logger_conf.Log.logger


class PathFinder:
    """Classe qui fournit les chemins des fichiers en fonction du contexte (en développement, en .exe...)"""
    @staticmethod
    def get_cache_directory() -> str:
        # Si l'application est en .exe
        if getattr(sys, 'frozen', False):
            # logger.info("Twysn is frozen")

            datadir = os.path.dirname(sys.executable)  # Répertoire de l'exécutable
            # logger.info(datadir)


            chemin_absolu = datadir + "/data/cache"
            if not os.path.exists(chemin_absolu):
                os.makedirs(chemin_absolu)
            # logger.info(chemin_absolu)
            # logger.info(os.path.abspath(chemin_absolu))
            return chemin_absolu

        # Si l'application est en développement
        else:
            chemin_relatif = "/../data/cache"
            chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)
            if not os.path.exists(chemin_absolu):
                os.makedirs(chemin_absolu)
            print(chemin_absolu)
            return chemin_absolu
            # logger.info("Twysn isn't frozen, secret file : " + chemin_app_tokens)

    @staticmethod
    def get_icon_path():
        if getattr(sys, 'frozen', False):
            frozen = True
            chemin_relatif = "twisn.png"
            chemin_absolu = os.path.abspath(os.path.dirname(sys.executable) + "/" + chemin_relatif)
        else:
            frozen = False
            chemin_relatif = "/../assets/twisn.png"
            chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)
        return frozen, chemin_absolu

    @staticmethod
    def get_app_tokens_file() -> str:
        if getattr(sys, 'frozen', False):
            chemin_relatif = "app_tokens"
            chemin_absolu = os.path.abspath(os.path.dirname(sys.executable) + "/" + chemin_relatif)
            # logger.info("Twysn is frozen, " + chemin_relatif + " file : " + chemin_absolu)

        else:
            chemin_relatif = "/../assets/app_tokens"
            chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)
            # logger.info("Twysn is frozen, " + chemin_relatif + " file : " + chemin_absolu)
        return chemin_absolu

    @staticmethod
    def get_user_tokens_file() -> str:
        if getattr(sys, 'frozen', False):
            chemin_relatif = "data/user_tokens"
            chemin_absolu = os.path.abspath(os.path.dirname(sys.executable) + "/" + chemin_relatif)
            # logger.info("Twysn is frozen, " + chemin_relatif + " file : " + chemin_absolu)

        else:
            chemin_relatif = "/../data/user_tokens"
            chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)
            # logger.info("Twysn is frozen, " + chemin_relatif + " file : " + chemin_absolu)
        return chemin_absolu

    @staticmethod
    def get_data_directory() -> str:
        if getattr(sys, 'frozen', False):
            chemin_relatif = "secrets"
            chemin_absolu = os.path.abspath(os.path.dirname(sys.executable) + "/" + chemin_relatif)
            # logger.info("Twysn is frozen, secret file : " + chemin_app_tokens)

        else:
            chemin_relatif = "/../data/secrets"
            chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)
            # logger.info("Twysn isn't frozen, secret file : " + chemin_app_tokens)
        return chemin_absolu
