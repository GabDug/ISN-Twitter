import os.path

cheminrelatif = 'secrets'
cheminabsolu = os.path.abspath(cheminrelatif)
#print(cheminabsolu)

def existfile():
    return os.path.exists(cheminabsolu)

def existlines(): #verifier que lignes pas vides
    with open('data.txt') as f:
        for n in range (0,len(f)):
            if f[n] == "":
            else:
                
def existtokens():
    nb_ligne:
    if fich[0] == ""
    try:
        
    except IOError:
        print("Erreur! Le fichier n'a pas le bon nombre de ligne")
    return

if __name__=="__main__":
    print(existfile())



#   try:
##        with open('fichier'): pass
##        except IOError:
##            print("Erreur! Le fichier n'a pas pu être ouvert")
##    return(booleen)
