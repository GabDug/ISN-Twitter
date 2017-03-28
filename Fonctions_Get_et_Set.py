import base64
import secrets


def encode():
#récupère tokens à partir de secrets et les crypte en b64 dans une liste
    data = open('D:\Quentin\ISN-Twitter\secrets', 'r').readlines()
    a = base64.encodestring(data[0].encode('ascii'))
    b = base64.encodestring(data[1].encode('ascii'))
    c = base64.encodestring(data[2].encode('ascii'))
    d = base64.encodestring(data[3].encode('ascii'))
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


def settoken():
#permet de changer les valeurs des usertokens dans le fichier secrets
    data = open('D:\Quentin\ISN-Twitter\secrets', 'r').readlines()
    data[2] = str(input("OAUTH_TOKEN : "))+'\n'
    data[3] = str(input("OAUTH_TOKEN_SECRET : "))+'\n'
    out = open('D:\Quentin\ISN-Twitter\secrets', 'w')
    out.writelines(data)
    out.close()

#les tests, tu peux décommenter si tu veux essayer :)
'''
liste = encode()#on crée une liste contenant les tokens provenant de secrets sous forme cryptée b64
print(liste)
gettoken(liste)#on décrypte la liste
print(liste)
liste = encode()#on réinitialise la liste (pour y voir plus clair)
settoken()#on change les usertokens (par bite)
liste = encode()
print(liste)
gettoken(liste)#on décrypte la nouvelle liste
print(liste)
'''

