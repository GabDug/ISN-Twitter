import base64
import os.path

# ATTENTION!
# Ne pas appeler le module "token" car ça override le module token de python et crée des erreurs


# TODO Vérifier sur d'autres OS
# Code nécessaire car le chemin était différent si lancé depuis token_manager ou depauis main_app avec l'ancienne
# implantation
chemin_relatif = "/../data/secrets"
chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)


def get_all_tokens() -> list:
    """
    Renvoie les 4 tokens (app et usr) stockés dans un fichier, dans une liste :
    TWITTER_APP_KEY, TWITTER_APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    """
    f = open(chemin_absolu, 'r')
    data = f.readlines()
    decoded = _decoder(data)
    f.close()
    return decoded


def get_app_tokens() -> list:
    """
    Renvoie les 4 tokens (app et usr) stockés dans un fichier, dans une liste :
    TWITTER_APP_KEY, TWITTER_APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    """
    f = open(chemin_absolu, 'r')
    l = []
    for i in range(2):
        l.append(f.readline())
    decoded = _decoder(l)
    f.close()
    return decoded


# On spécifie que les arguments sont des str et que la fonction renvoie un bool
def set_tokens(token1: str, token2: str) -> bool:
    """Permet de changer les tokens utilisateurs qui sont stockés dans un fichier."""
    # TODO utiliser une seule lecture/écriture du fichier
    # TODO Utiliser with open pour ne pas à avoir à fermer le fichier (cf lien)
    # http://python-guide-pt-br.readthedocs.io/en/latest/writing/style/#read-from-a-file
    f = open(chemin_absolu, 'r')
    data = f.readlines()
    if len(data) == 2:
        data.append(_encoder(token1))
        data.append(_encoder(token2))
    elif len(data) == 4:
        data[2] = _encoder(token1)
        data[3] = _encoder(token2)
    else:
        print("WARNING ! TOKEN FILE NOT SUPPORTED ! ")
    f.close()

    fout = open(chemin_absolu, 'w')
    fout.writelines(data)
    fout.close()

    # TODO Retourne True si le changement a bien été effectué
    return True


def user_token_exist() -> bool:
    """Renvoie True si les tokens app et usr sont sauvegardés."""
    f = open(chemin_absolu, 'r')
    data = f.readlines()
    if len(data) < 4:
        return False
    elif len(data) == 4:
        return True


# crypte les str par lequelles on va remplacer les usertokens
def _encoder(texte: str) -> str:
    return (base64.encodebytes(texte.encode('ascii'))).decode('unicode_escape')


# décrypte chaque élément de la liste dans une nouvelle liste
def _decoder(liste: list) -> list:
    # TODO Remplacer par une boucle
    # TODO Ajouter mécanisme pour enlever les = (et les rajouter)
    for i in range(len(liste)):
        liste[i] = (base64.decodebytes(liste[i].encode())).decode('unicode_escape')
    return liste


def _set_app_tokens(token1: str, token2: str) -> bool:
    """Permet de changer les tokens app qui sont stockés dans un fichier. Maintenance uniquement"""
    f = open(chemin_absolu, 'r')
    data = f.readlines()
    data[0] = _encoder(token1)
    data[1] = _encoder(token2)
    f.close()

    fout = open(chemin_absolu, 'w')
    fout.writelines(data)
    fout.close()

    return True


# TODO Vérifier taille des listes, présence du fichier, population du fichier => empêcher toutes les erreurs

# Tests
if __name__ == "__main__":
    # print(get_all_tokens())
    # a = input("Token 0")
    # b = input("Token 1")
    # set_tokens(a, b)
    # print(get_all_tokens())
    print(get_all_tokens())
