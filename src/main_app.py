import logging
import threading
import tkinter as tk
from sys import stdout
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

import mttkinter as tk
from src import ITwython
from src import auth_gui
from src import token_manager


# from tkinter.ttk import *


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
        self.cadre_tweet.grid(column=0, row=0)

        self.tl = TimeLine(self)
        self.tl.grid(column=1, row=0)


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

        # TODO Utiliser un champ Text
        self.texte = Label(self, text="Nouveau tweet :")
        self.tweet = Entry(self, textvariable=self.tweet_message)
        self.bouton = Button(self, text="Tweeter", command=self.tweeter)
        self.message = Label(self, textvariable=self.message_resultat)

        self.texte.grid(column=0, row=0)
        self.tweet.grid(column=0, row=1)
        self.bouton.grid(column=0, row=2)
        self.message.grid(column=0, row=3)

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

    def __init__(self, parent, data):
        print("Initialisation cadre : tweet")
        Frame.__init__(self, parent)
        self.parent = parent
        # self.connec = parent.connec

        # On met en place le cadre du tweet
        self.data = data

        screen_name = data["user"]["screen_name"].encode("utf-8").decode('utf-8')
        name = data["user"]["name"].encode("utf-8").decode('utf-8')
        status = data['text'].encode("utf-8").decode('utf-8')
        date = data["created_at"].encode("utf-8").decode('utf-8')

        # self.profile_image = Label(self, image=None)
        try:
            self.status = Message(self, text=status, width=200)
        except tk.TclError as e:
            self.status = Message(self, text=status.encode("utf-8"), width=200)
            print(e)

        try:
            self.name = Label(self, text=name)
        except tk.TclError as e:
            print(e)
            self.name = Label(self, text=name.encode("utf-8"))
        try:
            self.screen_name = Label(self, text="@" + screen_name)
        except tk.TclError as e:
            print(e)
        self.date = Label(self, text=date)
        # self.fav_count = Label(self, text="0")
        # self.rt_count = Label(self, text="1")

        # self.profile_image.pack()
        self.name.pack()
        self.screen_name.pack()
        self.status.pack()
        self.date.pack()
        # self.fav_count.pack()
        # self.rt_count.pack()


class TimeLine(Frame):
    def __init__(self, parent):
        print("Initialisation cadre : timeline")
        Frame.__init__(self, parent)
        self.parent = parent

        # J'ai mis le canvas en bleu pour bien voir là où il est : on est pas censé le voir mais juste le frame
        # On utilise un frame dans un canvas car pas de scrollbar sur le frame => scrollbar sur canvas
        self.canvas = Canvas(self, borderwidth=0, width=210, background="blue")
        self.frame = Frame(self.canvas)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.grid(column=1, row=0, sticky="nes")
        self.canvas.grid(column=0, row=0, sticky="nesw")
        self.canvas.create_window((4, 4), window=self.frame,
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.ligne = 0

        self.streamer = ITwython.MyStreamer(self, parent.app_key, parent.app_secret,
                                            parent.user_key, parent.user_secret)

        def async_stream():
            # On utilise une autre notation que with="followings" car with est un mot clé réservé de python
            # Sinon on doit modifier le fichier helper de la librairie twython => hack sale
            # On utilise un unpacking avec double splat http://deusyss.developpez.com/tutoriels/Python/args_kwargs/
            self.streamer.user(**{"with": "followings"})

        # On défini le thread comme daemon : dépend du thread principal, se ferme si le principal quitte
        thread_tl = threading.Thread(target=async_stream, daemon=True)
        thread_tl.start()

        # À utiliser pour debuguer, il faut commenter tout ce qui est async et connexion
        # self.peupler()

    def peupler(self):
        """Ajoute de fausses données pour travailler sur la mise en page hors-ligne,"
        " pour empecher de se faire bloquer par Twitter à force de recréer des connexions."""
        data = [
            {
                "text": "Franklin sait faire ses lacets et compter jusqu'à dix.",
                "created_at": "Le 38 mai",
                'user': {"screen_name": "sofolichon", "name": "Poutou <3"}},
            {
                "text": "123456789012345678901234567890123456789012345678901234"
                        "5678901234567890123456789012345678901234567890",
                "created_at": "19 janvier 2901",
                'user': {"screen_name": "PPDA", "name": "Patrick"}},
            {
                "text": "ONE TWO THREE, VIVA L'ALGERIE",
                "created_at": "1er mai 2000",
                'user': {"screen_name": "Karisss", "name": "Mastik"}},
            {
                "text": "Lorem ipsum, j'aime les grenouilles, mange ma quenouille",
                "created_at": "Le 20 avril",
                'user': {"screen_name": "Kmi", "name": "Grand fou"}},
            {
                "text": "Ça marche aussi avec les messages qui se rapprochent de 140 caractères ou,"
                        "encore mieux, ceux qui font exactement cent-quarante caractères !",
                "created_at": "15/04/2017 18:49",
                'user': {"screen_name": "DUGNYCHON", "name": "Gabi"}}
        ]

        # On ajoute les données normalement
        for fake_tweet in data:
            self.add_data(fake_tweet)

    def add_data(self, data):
        """Ajoute un objet Tweet à la TimeLine."""
        if 'text' in data:
            tweet = Tweet(self.frame, data)
            tweet.grid(row=self.ligne, column=0)
            print(self.ligne)
            self.ligne = self.ligne + 1
            # self.scrollbar.grid_configure(rowspan=self.ligne + 1)

    def onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


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

    App(principal).grid(sticky="nsew")
    principal.mainloop()
    logging.info("TWISN CLOSED")
