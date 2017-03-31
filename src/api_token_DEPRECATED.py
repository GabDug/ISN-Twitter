import base64

from data import secret as s


def existe():
    return True


def encode(couple):
    print("Coding token...")
    # Récupère tokens à partir de s et les crypte en b64 dans une liste base64.encodebytes(couple[0].encode('ascii'))
    s.OAUTH_TOKEN = "2"
    s.OAUTH_TOKEN_SECRET = base64.encodebytes(couple[1].encode('ascii'))


def decode():
    # Décrypte chaque élément de la liste dans une nouvelle liste
    liste = []
    liste.append (base64.decodebytes(s.TWITTER_APP_KEY).decode('unicode_escape'))
    liste.append(base64.decodebytes(s.TWITTER_APP_SECRET).decode('unicode_escape'))
    liste.append(base64.decodebytes(s.OAUTH_TOKEN).decode('unicode_escape'))
    liste.append(base64.decodebytes(s.OAUTH_TOKEN_SECRET).decode('unicode_escape'))
    return liste


def get_token():
    # récupère la liste cryptée par encode et appelle la fonction decode
    decoded = decode()
    return decoded  # liste


def set_token(couple):
    print("Setting token...")
    # remplace les usertokens par de nouveaux tokens dans la liste créée par encode
    encode(couple)


# les tests, tu peux décommenter si tu veux essayer :)
c = []
c.append("2862904287-pTHefLZc3hG1QNgVfGES9ZbqOnZIylobzsPDm3w")
c.append("aJq2GkNXg9L6WQ5XYIl09L0cj9rnSW8i7Un5126rGLuuB")
s.OAUTH_TOKEN ="111"
set_token(c)
# liste = encode()  # on crée une liste contenant les tokens provenant de s sous forme cryptée b64
# print(liste)
# gettoken(liste)  # on décrypte la liste
# print(liste)
# liste = encode()  # on réinitialise la liste (pour y voir plus clair)
# settoken(liste)  # on change les usertokens (par bite)
# print(liste)
# gettoken(liste)  # on décrypte la nouvelle liste
# print(liste)  # et la y a marqué 000 c'est drôle :)
