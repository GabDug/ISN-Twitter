from tkinter import *
from tkinter.ttk import *
import ITwython
import auth_gui


# Structure d'après
# https://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application
class App(Frame):
    def __init__(self, parent):
        # On définit le cadre dans l'objet App
        Frame.__init__(self, parent)

        # On met en paramètre le parent et la connexion Twytho
        self.parent = parent
        self.connec = ITwython.Connec()

        # TODO On vérifie si on doit créer une nouvelle connexion ou si on doit charger les tokens
        auth_gui.fenetreconnexion()

        # TODO Supprimer prototype pour envoyer tweets
        tw = StringVar()

        texte = Label(self, text="Rédigez votre tweet : ")
        tweet = Entry(self, textvariable=tw)
        bouton = Button(self, text="Envoyer", command=lambda: ITwython.Connec.tweeter(self.connec, tw.get()))
        texte.pack()
        tweet.pack()
        bouton.pack()


# On commence le code ici
if __name__ == "__main__":
    # Principal est la racine de l'app
    principal = Tk()
    principal.title("TwISN")
    principal.config(bg='white')
    # on ne travaille pas directement dans principal
    # mais on utilise un cadre (Objet App
    App(principal).pack(side="top", fill="both", expand=True)
    principal.mainloop()
