import base64
import os.path
import sys

import logger_conf

logger = logger_conf.Log.logger

# ATTENTION!
# Ne pas appeler le module "token" car ça override le module token de python et crée des erreurs


# TODO Vérifier sur d'autres OS
# Code nécessaire car le chemin était différent si lancé depuis token_manager
# ou depuis main_app avec l'ancienne implantation

if getattr(sys, 'frozen', False):
    # The application is frozen
    datadir = os.path.dirname(sys.executable)
    chemin_relatif = "secrets"
    chemin_absolu = os.path.abspath(os.path.dirname(sys.executable) + "/" + chemin_relatif)
    logger.info("Twysn is frozen, secret file : " + chemin_absolu)

else:
    # The application is not frozen
    # Change this bit to match where you store your data files:
    chemin_relatif = "/../data/secrets"
    chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)
    logger.info("Twysn isn't frozen, secret file : " + chemin_absolu)


def get_all_tokens() -> list:
    """
    Renvoie les 4 tokens (app et usr) stockés dans un fichier, dans une liste :
    TWITTER_APP_KEY, TWITTER_APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    """
    try:
        with open(chemin_absolu, 'r') as f:
            data = f.readlines()
            decoded = _decoder_liste(data)
            return decoded
    except IOError:
        logger.error("Erreur ! Le fichier n'a pas pu être ouvert")  # on verifie si le fichier existe
        return


def get_app_tokens() -> list:
    """
    Renvoie les 4 tokens (app et usr) stockés dans un fichier, dans une liste :
    TWITTER_APP_KEY, TWITTER_APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    """
    try:
        with open(chemin_absolu, 'r') as f:
            l = []
            for i in range(2):
                l.append(f.readline())
            decoded = _decoder_liste(l)
        return decoded
    except IOError as e:
        logger.error("Erreur! Le fichier n'a pas pu être ouvert")  # on verifie si le fichier existe
        return

# On spécifie que les arguments sont des str et que la fonction renvoie un bool
def set_tokens(token1: str, token2: str) -> bool:
    # http://python-guide-pt-br.readthedocs.io/en/latest/writing/style/#read-from-a-file
    try:
        with open(chemin_absolu, 'r+') as f:
            data = f.readlines()
            if len(data) == 4:
                data[2] = _encoder(token1)
                data[3] = _encoder(token2)
                # logger.debug(data)
            elif len(data) == 2:
                data.append(_encoder(token1))
                data.append(_encoder(token2))
                # logger.debug(data)
            else:
                logger.debug("WARNING ! TOKEN FILE NOT SUPPORTED ! ")
            f.truncate(0)  # on efface le contenu du fichier
            f.writelines(data)  # puis on ecrit le nouveau contenu
            return True
    except IOError:
        logger.debug("Erreur! Le fichier n'a pas pu être ouvert")  # on verifie si le fichier existe
        return False
    return False

def user_token_exist() -> bool:
    """Renvoie True si les tokens app et usr sont sauvegardés."""
    try:
        with open(chemin_absolu, 'r') as f:
            data = f.readlines()
            if len(data) < 4:
                return False
            elif len(data) == 4:
                return True
    except IOError:
        logger.debug("Erreur! Le fichier n'a pas pu être ouvert")  # on verifie si le fichier existe
        return False
    return False

# crypte les str par lequelles on va remplacer les usertokens
def _encoder(texte: str) -> str:
    encoded = (base64.encodebytes(texte.encode('ascii'))).decode('unicode_escape')
    encoded = encoded.replace("=", "")
    return encoded


def _decoder_string(element: str) -> str:
    element = element.replace('\n', '').replace('\r', '')
    missing_padding = 4 - ((len(element)) % 4)
    if missing_padding != 0:
        element += '=' * missing_padding

    element = (base64.decodebytes(element.encode())).decode('unicode_escape')
    return element


# décrypte chaque élément de la liste dans une nouvelle liste
def _decoder_liste(liste: list) -> list:
    """Décode une liste de strings en base 64."""
    # http://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding
    resultat = []
    for element in liste:
        resultat.append(_decoder_string(element))
    return resultat


def _set_app_tokens(token1: str, token2: str) -> bool:
    """Permet de changer les tokens app qui sont stockés dans un fichier. Maintenance uniquement"""
    try:
        with open(chemin_absolu, 'r+') as f:
            data = f.readlines()
            data[0] = _encoder(token1)
            data[1] = _encoder(token2)
            f.truncate(0)  # on efface le contenu du fichier
            f.writelines(data)  # puis on ecrit le nouveau contenu
    except IOError:
        logger.debug("Erreur! Le fichier n'a pas pu être ouvert")  # on verifie si le fichier existe
    return True


def _compterligne():
    try:
        with open(chemin_absolu, 'r') as f:
            nb_ligne = 0
            for line in f:
                nb_ligne += 1
            return nb_ligne
    except IOError:
        logger.debug("Erreur! Le fichier n'a pas pu être ouvert !")  # on verifie si le fichier existe
        return


# Tests
if __name__ == "__main__":
    logger.info(get_all_tokens())
    a = input("Token 0 :")
    b = input("Token 1 :")
    _set_app_tokens(a, b)
    # set_tokens(a,b)
    logger.info(get_all_tokens())
