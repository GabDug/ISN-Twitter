import base64
import os.path

# ATTENTION!
# Ne pas appeler le module "token" car ça override le module token de python et crée des erreurs


# TODO Vérifier sur d'autres OS
# Code nécessaire car le chemin était différent si lancé depuis token_manager ou depauis main_app avec l'ancienne
# implantation
chemin_relatif = "/../data/secrets"
chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)


def get_tokens() -> list:
    """Renvoie les 4 tokens (app et usr) stockés dans un fichier, dans une liste :
    TWITTER_APP_KEY, TWITTER_APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET"""
    f = open(chemin_absolu, 'r')
    data = f.readlines()
    decoded = decoder(data)
    f.close()
    return decoded


# On spécifie que les arguments sont des str et que la fonction renvoie un bool
def set_tokens(token1: str, token2: str) -> bool:
    """Permet de changer les tokens utilisateurs qui sont stockés dans un fichier."""
    # TODO utiliser une seule lecture/écriture du fichier
    f = open(chemin_absolu, 'r')
    data = f.readlines()
    data[2] = encoder(token1)
    data[3] = encoder(token2)
    f.close()

    fout = open(chemin_absolu, 'w')
    fout.writelines(data)
    fout.close()

    # TODO Retourne True si le changement a bien été effectué
    return True


def user_token_exist() -> bool:
    """Renvoie True si les tokens app et usr sont sauvegardés."""
    # TODO Fonction exist
    return True


def encoder(texte: str) -> str:
    # crypte les str par lequelles on va remplacer les usertokens
    return (base64.encodebytes(texte.encode('ascii'))).decode('unicode_escape')


def decoder(liste: list) -> list:
    # décrypte chaque élément de la liste dans une nouvelle liste
    # TODO Remplacer par une boucle
    liste[0] = (base64.decodebytes(liste[0].encode())).decode('unicode_escape')
    liste[1] = base64.decodebytes(liste[1].encode()).decode('unicode_escape')
    liste[2] = base64.decodebytes(liste[2].encode()).decode('unicode_escape')
    liste[3] = base64.decodebytes(liste[3].encode()).decode('unicode_escape')
    return liste


# TODO Vérifier taille des listes, présence du fichier, population du fichier => empêcher toutes les erreurs

# Tests
if __name__ == "__main__":
    print(get_tokens())
