import logging
import tkinter as tk
from sys import stdout
from tkinter.ttk import *

from src import ITwython
from src import auth_gui
from src import token_manager


# Structure d'après
# https://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application
# Classe qui hérite de Frame

def final(fenetre, connectemporaire, oauth_verifier):
    login_credentials = connectemporaire.final(oauth_verifier)
    user_token, user_token_secret = login_credentials["oauth_token"], login_credentials["oauth_token_secret"]
    print("Oauth Token : {0}, Oauth Token Secret : {1}".format(user_token, user_token_secret))
    token_manager.set_tokens(user_token, user_token_secret)
    print(token_manager.get_all_tokens())
    fenetre.destroy()


class App(Frame):
    def __init__(self, parent):
        # On définit le cadre dans l'objet App (inutile car pas kwargs**...)
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.lift()

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

        self.ajout_widget()

    def ajout_widget(self):
        self.cadre_tweet = NouveauTweet(self)
        self.cadre_tweet.pack()


class NouveauTweet(Frame):
    """Définit le cadre avec les widgets pour envoyer un tweet, ainsi que les fonctions pour répondre aux actions des
    boutons des widgets nécessaires (bouton envoyer...)"""

    def __init__(self, parent):
        print("Initialisation cadre : nouveau tweet")
        Frame.__init__(self, parent)
        self.parent = parent
        self.connec = parent.connec

        # On met en place le cadre du tweet
        self.tweet_message = tk.StringVar()
        self.message_resultat = tk.StringVar()

        texte = Label(self, text="Nouveau tweet :")
        self.tweet = Entry(self, textvariable=self.tweet_message)
        self.bouton = Button(self, text="Tweeter", command=self.tweeter)
        self.message = Label(self, textvariable=self.message_resultat)

        texte.pack()
        self.tweet.pack()
        self.bouton.pack()
        self.message.pack()

    def tweeter(self):
        message = self.tweet_message.get()
        self.tweet.state(["disabled"])
        self.bouton.state(["disabled"])
        print("Désactivé")

        # définir une fonction là sert à rien pour le moment mais peut être plus atdr pour le multithreading
        def action():
            self.connec.tweeter(self, message)

            # self.message_resultat.set(msg__)
            # print("A :" + str(bool__))
            # print("B :" + str(msg__))
            # self.tweet.state(["!disabled"])
            # self.bouton.state(["!disabled"])

        action()
        # TODO Activer/désactiver marche pas

    # Executé après l'envoi
    # __ c'est un paramètre plus utilisé que j'avais la flemme d'enlever
    def callback(self, succes: bool, msg_, __=None):
        print("Début callback")
        self.message_resultat.set(msg_)
        # self.tweet.state(["disabled"])
        # self.bouton.state(["disabled"])
        print("Réactivé")


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
    # On crée un logger : c'est pour gérer les logs de l'application
    # Je vais essayer de remplacer tous les print() par des logger.info() ou logger.warning() etc
    # Ca permet plus de clarté (ce qui est normal ou pas...) et de mettre dans un fichier
    # Ca permet aussi d'avoir le moment précis de tel ou tel message pour savoir où on en est dans le code (pratique!)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(stdout)
    ch.setLevel(logging.DEBUG)

    f = logging.FileHandler("twisn.log", mode="w", level=logging.DEBUG)
    f.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(funcName)s in %(filename)s] : %(message)s")

    ch.setFormatter(formatter)
    f.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(f)

    # logging.basicConfig(filename='twisn.log', filemode='w',
    #                     format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%H:%M:%S",
    #                     level=logging.INFO)
    # logging.debug('This message should go to the log file')
    # logging.info('So should this')
    # logging.warning('And this, too')
    # logging.info("TWISN STARTED")
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')

    # Fin de la définition du logger

    # Principal est la racine de l'app
    principal = tk.Tk()
    principal.title("TwISN")
    principal.config(bg='white')

    # on ne travaille pas directement dans principal
    # mais on utilise un cadre (Objet App)

    App(principal).pack(side="top", fill="both", expand=True)
    principal.mainloop()
    logging.info("TWISN CLOSED")
