from tkinter import *
from tkinter.ttk import *

from src import ITwython
from src import auth_gui
from src import token_manager


# Structure d'après
# https://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application
# Classe qui hérite de Frame

def final(connectemporaire, oauth_verifier):
    login_credentials = connectemporaire.final(oauth_verifier)
    user_token, user_token_secret = login_credentials["oauth_token"], login_credentials["oauth_token_secret"]
    print("Oauth Token : {0}, Oauth Token Secret : {1}".format(user_token, user_token_secret))
    token_manager.set_tokens(user_token, user_token_secret)
    print(token_manager.get_all_tokens())


class App(Frame):
    def __init__(self, parent):
        # On définit le cadre dans l'objet App (inutile car pas kwargs**...)
        Frame.__init__(self, parent)

        # On met en paramètre le parent et la connexion Twython
        self.parent = parent

        # TODO On vérifie si on doit créer une nouvelle connexion ou si on doit charger les tokens

        # Tant que les tokens n'existent pas alors ouvrir fenêtre de connexion
        if not token_manager.user_token_exist():
            app_key, app_secret = token_manager.get_app_tokens()
            connectemp = ITwython.ConnecTemporaire(app_key, app_secret)
            auth_url = connectemp.auth_url

            auth_window = auth_gui.FenetreConnexion(connectemp, auth_url).root
            auth_window.grab_set()
            principal.wait_window(auth_window)

        # On récupère les différents tokens
        # On est normalement assuré des 4 éléments donc on peux utiliser l'unpacking
        # http://python-guide-pt-br.readthedocs.io/en/latest/writing/style/#unpacking
        app_key, app_secret, user_key, user_secret = token_manager.get_all_tokens()
        # Une fois qu'on a les tokens, créer la connexion
        self.connec = ITwython.Connec(app_key, app_secret, user_key, user_secret)

        # TODO Focus sur la fenêtre



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
