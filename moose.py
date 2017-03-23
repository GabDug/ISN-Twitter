import base64
import secrets


def encode():
#récupère tokens à partir de secrets et les crypte en b64 dans une liste
    a = base64.encodestring(secrets.TWITTER_APP_KEY.encode('ascii'))
    b = base64.encodestring(secrets.TWITTER_APP_SECRET.encode('ascii'))
    c = base64.encodestring(secrets.OAUTH_TOKEN.encode('ascii'))
    d = base64.encodestring(secrets.OAUTH_TOKEN_SECRET.encode('ascii'))
    encoded = [a,b,c,d]
    return encoded#liste


def encoder(texte):
#crypte les str par lequelles on va remplacer les usertokens
    return base64.encodestring(texte.encode('ascii'))


def decode(liste):
#décrypte chaque élément de la liste dans une nouvelle liste
    liste[0] = base64.decodestring(liste[0]).decode('unicode_escape')
    liste[1] = base64.decodestring(liste[1]).decode('unicode_escape')
    liste[2] = base64.decodestring(liste[2]).decode('unicode_escape')
    liste[3] = base64.decodestring(liste[3]).decode('unicode_escape')
    return liste

    
def gettoken(liste):
#récupère la liste cryptée par encode et appelle la fonction decode
    decoded = decode(liste)
    return decoded#liste


def settoken(liste):
#remplace les usertokens par de nouveaux tokens dans la liste créée par encode
    liste[2] = encoder('bite')
    liste[3] = encoder(secrets.OAUTH_TOKEN_SECRET)



#les tests, tu peux décommenter si tu veux essayer :)
'''
liste = encode()#on crée une liste contenant les tokens provenant de secrets sous forme cryptée b64
print(liste)
gettoken(liste)#on décrypte la liste
print(liste)
liste = encode()#on réinitialise la liste (pour y voir plus clair)
settoken(liste)#on change les usertokens (par bite)
print(liste)
gettoken(liste)#on décrypte la nouvelle liste
print(liste)#et la y a marqué bite c'est drôle :)
'''
