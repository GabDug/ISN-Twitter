import logging
import threading
import tkinter as tk
from sys import stdout
from tkinter import messagebox
from tkinter.ttk import *

import mttkinter as tk
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
        self.app_key, self.app_secret, self.user_key, self.user_secret = token_manager.get_all_tokens()
        # Une fois qu'on a les tokens, créer la connexion
        self.connec = ITwython.Connec(self.app_key, self.app_secret, self.user_key, self.user_secret)

        self.ajout_widget()

    def ajout_widget(self):
        self.cadre_tweet = EnvoiTweet(self)
        self.cadre_tweet.pack()

        self.tl = TimeLine(self)
        self.tl.pack()


class EnvoiTweet(Frame):
    """Définit le cadre avec les widgets pour envoyer un tweet, ainsi que les fonctions pour répondre aux actions des
    boutons des widgets nécessaires (bouton envoyer...)"""

    def __init__(self, parent):
        print("Initialisation cadre : envoi de tweet")
        Frame.__init__(self, parent)
        self.parent = parent
        self.connec = parent.connec

        # On met en place le cadre d'envoi de tweet
        self.tweet_message = tk.StringVar()
        self.message_resultat = tk.StringVar()

        self.texte = Label(self, text="Nouveau tweet :")
        self.tweet = Entry(self, textvariable=self.tweet_message)
        self.bouton = Button(self, text="Tweeter", command=self.tweeter)
        self.message = Label(self, textvariable=self.message_resultat)

        self.texte.pack()
        self.tweet.pack()
        self.bouton.pack()
        self.message.pack()

    def tweeter(self):
        # On récupère le message depuis le widget d'entrée de texte
        message = self.tweet_message.get()

        def action_async():
            logger.info("Entering action")

            # On désactive l'entrée utilisateur pendant l'envoi du tweet
            self.tweet.state(["disabled"])
            self.bouton.state(["disabled"])

            # On lance le tweet via ITwython
            succes, msg = self.connec.tweeter(message)

            logger.debug("succes : " + str(succes))
            logger.debug("msg : " + str(msg))

            # On lance les actions de retour
            self.callback(succes, msg)
            logger.warning("Action done")

        # On lance l'action du tweet dans un thread asynchrone
        th = threading.Thread(target=action_async)
        th.start()

    def callback(self, succes: bool, msg_):
        """Éxecuté après l'envoi"""
        logger.debug("Début callback")

        # Si le tweet a bien été envoyé
        if succes:
            self.message_resultat.set(msg_)
        # Si il y a eu une erreur
        else:
            messagebox.showerror(
                "Impossible d'envoyer le tweet",
                "Erreur : {0}".format(msg_)
            )

        # On réactive l'entrée utilisateur
        self.tweet.state(["!disabled"])
        self.bouton.state(["!disabled"])
        logger.debug("Fin callback")


class Tweet(Frame):
    """Cadre pour afficher un tweet unique."""

    def __init__(self, parent, screen_name: str, name: str, status, date: str):
        print("Initialisation cadre : tweet")
        Frame.__init__(self, parent)
        self.parent = parent
        # self.connec = parent.connec
        print(screen_name)
        print(name)
        print(status)
        print(date)
        repr(screen_name)
        repr(name)
        repr(status)
        repr(date)

        # On met en place le cadre du tweet
        self.tweet_message = tk.StringVar()
        self.message_resultat = tk.StringVar()

        # self.profile_image = Label(self, image=None)
        self.status = Label(self, text=status)
        self.name = Label(self, text=name)
        self.screen_name = Label(self, text=screen_name)
        self.date = Label(self, text=date)
        # self.fav_count = Label(self, text="0")
        # self.rt_count = Label(self, text="1")

        # self.profile_image.pack()
        self.status.pack()
        self.name.pack()
        self.screen_name.pack()
        self.date.pack()
        # self.fav_count.pack()
        # self.rt_count.pack()


class TimeLine(Frame):
    def __init__(self, parent):
        print("Initialisation cadre : timeline")
        Frame.__init__(self, parent)
        self.parent = parent
        # TODO Définir un streamer par bloc car on ne peux l'utiliser que pour un bloc
        self.streamer = ITwython.MyStreamer(parent.app_key, parent.app_secret,
                                            parent.user_key, parent.user_secret,
                                            self)

        def async_stream():
            # On utilise une autre notation que with="followings" car with est un mot clé réservé de python
            # Sinon on doit modifier le fichier helper de la librairie twython => hack sale
            self.streamer.user(**{"with": "followings"})

        # On défini le thread comme daemon : dépend du thread principal, se ferme si le principal quitte
        thread_tl = threading.Thread(target=async_stream, daemon=True)
        thread_tl.start()

    # On récupère une donnée brute, qu'on traite pour en faire un objet Tweet affiché
    def add_data(self, data):
        if 'text' in data:
            tweet = Tweet(self, data["user"]["screen_name"], data["user"]["name"], data['text'], data["created_at"])
            tweet.pack()


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

    f = logging.FileHandler("twisn.log", mode="w")
    f.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(funcName)s in %(filename)s] : %(message)s")
    formatter.datefmt = "%H:%M:%S"
    ch.setFormatter(formatter)
    f.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(f)

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
