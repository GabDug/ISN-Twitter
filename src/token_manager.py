import base64
import os.path

# ATTENTION!
# Ne pas appeler le module "token" car ça override le module token de python et crée des erreurs


# TODO Vérifier sur d'autres OS
# Code nécessaire car le chemin était différent si lancé depuis token_manager
# ou depuis main_app avec l'ancienne implantation
chemin_relatif = "/../data/secrets"
chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)


def get_all_tokens() -> list:
    """
    Renvoie les 4 tokens (app et usr) stockés dans un fichier, dans une liste :
    TWITTER_APP_KEY, TWITTER_APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    """
    try:
        with open(chemin_absolu, 'r') as f:
            data = f.readlines()
            decoded = _decoder(data)
    except IOError:
        print("Erreur! Le fichier n'a pas pu être ouvert")  # on verifie si le fichier existe
    return decoded


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
            decoded = _decoder(l)
    except IOError as e:
        print("Erreur! Le fichier n'a pas pu être ouvert")  # on verifie si le fichier existe
    return decoded


# On spécifie que les arguments sont des str et que la fonction renvoie un bool
def set_tokens(token1: str, token2: str) -> bool:
    # http://python-guide-pt-br.readthedocs.io/en/latest/writing/style/#read-from-a-file
    try:
        with open(chemin_absolu, 'r+') as f:
            data = f.readlines()
            if len(data) == 4:
                data[2] = _encoder(token1)
                data[3] = _encoder(token2)
                # print(data)
            elif len(data) == 2:
                data.append(_encoder(token1))
                data.append(_encoder(token2))
                # print(data)
            else:
                print("WARNING ! TOKEN FILE NOT SUPPORTED ! ")
            f.truncate(0)  # on efface le contenu du fichier
            f.writelines(data)  # puis on ecrit le nouveau contenu
    except IOError:
        print("Erreur! Le fichier n'a pas pu être ouvert")  # on verifie si le fichier existe
    return True


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
        print("Erreur! Le fichier n'a pas pu être ouvert")  # on verifie si le fichier existe


# crypte les str par lequelles on va remplacer les usertokens
def _encoder(texte: str) -> str:
    return (base64.encodebytes(texte.encode('ascii'))).decode('unicode_escape')


# décrypte chaque élément de la liste dans une nouvelle liste
def _decoder(liste: list) -> list:
    # TODO Ajouter mécanisme pour enlever les = (et les rajouter) voir lien :
    # http://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding
    for i in range(len(liste)):
        liste[i] = (base64.decodebytes(liste[i].encode())).decode('unicode_escape')
    return liste


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
        print("Erreur! Le fichier n'a pas pu être ouvert")  # on verifie si le fichier existe
    return True


def _compterligne():
    try:
        with open(chemin_absolu, 'r') as f:
            nb_ligne = 0
            for line in f:
                nb_ligne += 1
    except IOError:
        print("Erreur! Le fichier n'a pas pu être ouvert")  # on verifie si le fichier existe
    return nb_ligne


##    missing_padding = len(liste) % 4 #on regarde si c'est un multiple de 4
##    if missing_padding != 0:
##        liste[i] += b'='* (4 - missing_padding) #si non alors on ajoute des '=' pour quil le devienne
##    idée pour les '=' a ajouter/retirer, ne fonctionne pas, message d'erreur :
##    TypeError: Can't convert 'bytes' object to str implicitly


# Tests
if __name__ == "__main__":
    print(get_all_tokens())
    a = input("Token 0 :")
    b = input("Token 1 :")
    set_tokens(a, b)
    print(get_all_tokens())
