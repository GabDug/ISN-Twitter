import base64
import binascii
import os

import logger_conf
import path_finder

logger = logger_conf.Log.logger

# ATTENTION!
# Ne pas appeler le module "token" car ça override le module token de python et crée des erreurs


# Code nécessaire car le chemin était différent si lancé depuis token_manager
# ou depuis main_app avec l'ancienne implantation ou en .exe
chemin_app_tokens = path_finder.PathFinder.get_app_tokens_file()
chemin_user_tokens = path_finder.PathFinder.get_user_tokens_file()


def get_all_tokens() -> list:
    """
    Renvoie les 4 tokens (app et usr) stockés dans 2 fichiers, dans une liste :
    TWITTER_APP_KEY, TWITTER_APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    """
    app_tokens = get_app_tokens()
    user_tokens = get_user_tokens()
    return app_tokens + user_tokens


def get_app_tokens() -> list:
    """
    Renvoie les 2 tokens (app et usr) stockés dans un fichier, dans une liste :
    TWITTER_APP_KEY, TWITTER_APP_SECRET,
    """
    try:
        if os.path.isfile(chemin_app_tokens):
            with open(chemin_app_tokens, 'r') as f:
                l = []
                for i in range(2):
                    l.append(f.readline())
                decoded = _decoder_liste(l)
            return decoded
        else:
            logger.error("Pas de fichier '{0}' !".format(chemin_app_tokens))
            return ["", ""]
    except IOError as e:
        logger.error("Erreur ! Le fichier n'a pas pu être ouvert : " + e)  # on verifie si le fichier existe
        return ["", ""]


def get_user_tokens() -> list:
    """
    Renvoie les 2 tokens (app et usr) stockés dans un fichier, dans une liste :
    OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    """
    try:
        if os.path.isfile(chemin_user_tokens):
            with open(chemin_user_tokens, 'r') as f:
                l = []
                for i in range(2):
                    l.append(f.readline())
                decoded = _decoder_liste(l)
            return decoded
        else:
            logger.warning("Pas de fichier '{0}' !".format(chemin_user_tokens))
            return ["", ""]
    except IOError as e:
        logger.error("Erreur ! Le fichier n'a pas pu être ouvert : " + e)  # on verifie si le fichier existe
        return ["", ""]


def set_tokens(token1: str, token2: str) -> bool:
    # Doc : il faut utiliser with
    # http://python-guide-pt-br.readthedocs.io/en/latest/writing/style/#read-from-a-file
    try:
        with open(chemin_user_tokens, 'w') as f:
            f.write(_encoder(token1))
            f.write(_encoder(token2))
            return True
    except IOError as e:
        logger.error("Erreur ! Le fichier n'a pas pu être ouvert : " + e)
        return False


def delete_tokens():
    """Permet de supprimer les tokens de l'utilisateur, s'ils ne sont plus valables par exemple."""
    if os.path.isfile(chemin_user_tokens):
        os.remove(chemin_user_tokens)


def user_token_exist() -> bool:
    """Renvoie True si les tokens app et usr sont sauvegardés."""
    if os.path.isfile(chemin_user_tokens):
        return True
    else:
        return False


# crypte les str par lequelles on va remplacer les usertokens
def _encoder(texte: str) -> str:
    encoded = (base64.encodebytes(texte.encode('ascii'))).decode('unicode_escape')
    encoded = encoded.replace("=", "")
    return encoded


def _decoder_string(element: str) -> str:
    element = element.replace('\n', '').replace('\r', '').replace(' ', '')
    missing_padding = 4 - ((len(element)) % 4)
    if missing_padding != 0:
        element += '=' * missing_padding
    try:
        element = (base64.decodebytes(element.encode())).decode('unicode_escape')
        return element
    except binascii.Error as e:
        return ""


# Décrypte chaque élément de la liste dans une nouvelle liste
def _decoder_liste(liste: list) -> list:
    """Décode une liste de strings en base 64."""
    # http://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding
    resultat = []
    for element in liste:
        resultat.append(_decoder_string(element))
    return resultat


def _set_app_tokens(token1: str, token2: str) -> bool:
    """Permet de changer les tokens app qui sont stockés dans un fichier. Utilisée uniquement pour la maintenance."""
    try:
        with open(chemin_app_tokens, 'r+') as f:
            data = f.readlines()
            data[0] = _encoder(token1)
            data[1] = _encoder(token2)
            f.truncate(0)  # on efface le contenu du fichier
            f.writelines(data)  # puis on ecrit le nouveau contenu
            return True
    except IOError as e:
        logger.debug("Erreur ! Le fichier n'a pas pu être ouvert : " + e)  # on verifie si le fichier existe
        return False


# Tests
if __name__ == "__main__":
    logger.info(get_all_tokens())
    a = input("App Token 0 :")
    b = input("App Token 1 :")
    set_tokens(a, b)
    # set_tokens(a,b)
    logger.info(get_all_tokens())
