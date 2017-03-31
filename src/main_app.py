from tkinter import *
from tkinter.ttk import *

from src import ITwython


# import auth_gui
# import token2 as token

# Structure d'après
# https://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application
# Classe qui hérite de Frame

class App(Frame):
    def __init__(self, parent):
        # On définit le cadre dans l'objet App (inutile car pas kwargs**...)
        Frame.__init__(self, parent)

        # On met en paramètre le parent et la connexion Twython
        self.parent = parent

        # TODO On vérifie si on doit créer une nouvelle connexion ou si on doit charger les tokens

        # # Si les tokens n'existe pas alors ouvrir fenêtre de connexion
        # if not token.existe():
        #     auth_window = auth_gui.fenetreconnexion()
        #     auth_window.grab_set()
        #     principal.wait_window(auth_window)
        #
        # # Sinon on les récupère simplement
        # else:
        #     tok = token.get_token()
        # TODO Focus sur la fenêtre

        # self.connec = ITwython.Connec()
        #
        # TODO Supprimer prototype pour envoyer tweets
        tw = StringVar()

        texte = Label(self, text="Rédigez votre tweet : ")
        tweet = Entry(self, textvariable=tw)
        bouton = Button(self, text="Envoyer", command=lambda: ITwython.Connec.tweeter(self.connec, tw.get()))
        texte.pack()
        tweet.pack()
        bouton.pack()


# class Pri():
#     def __init__(self):
#         if True:
#             gui = auth_gui.fenetreconnexion()
#             gui.mainloop()
#
#     def maint(self):
#         principal = Tk()
#         principal.title("TwISN")
#         principal.config(bg='white')
#         # on ne travaille pas directement dans principal
#         # mais on utilise un cadre (Objet App)
#
#
#         App(principal).pack(side="top", fill="both", expand=True)
#         principal.mainloop()


# On commence le code ici
if __name__ == "__main__":
    # Principal est la racine de l'app
    principal = Tk()
    principal.title("TwISN")
    principal.config(bg='white')

    # on ne travaille pas directement dans principal
    # mais on utilise un cadre (Objet App)

    App(principal).pack(side="top", fill="both", expand=True)
    principal.mainloop()
