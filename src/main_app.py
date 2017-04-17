import threading
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

import ITwython
import auth_gui
import logger_conf
import mttkinter as tk
import token_manager
from ITwython import Tweet

logger = logger_conf.Log.logger


# TODO déplacer final dans App en staticmethod
def final(fenetre, connectemporaire, oauth_verifier):
    succes, login_credentials = connectemporaire.final(oauth_verifier)
    if succes:
        user_token, user_token_secret = login_credentials["oauth_token"], login_credentials["oauth_token_secret"]
        logger.debug("Oauth Token : {0}, Oauth Token Secret : {1}".format(user_token, user_token_secret))
        token_manager.set_tokens(user_token, user_token_secret)
        logger.debug(token_manager.get_all_tokens())
        fenetre.destroy()
    else:
        # TODO Voir
        logger.debug("Erreur à gérer")


# Structure d'après
# https://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application
# Classe qui hérite de Frame
class App(Frame):
    def __init__(self, parent, stream_connection=True, static_connection=True):
        """stream_connection et static_connection permettent d'activer ou de désactiver les deux types de connection
         pour travailler ur la mise en page sans se faire bloquer par les limitations."""
        # On définit le cadre dans l'objet App (inutile car pas kwargs**...)
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.lift()

        self.exist = True

        self.stream_connection = stream_connection
        self.static_connection = static_connection

        style = Style()
        style.configure("TLabel", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TFrame", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TEntry", foreground="black", background="#343232", font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 10))

        style.configure("Sidebar.TFrame", foreground="white", background="#111111", font=('Segoe UI', 10))
        style.configure("Sidebar.TLabel", foreground="white", background="#111111", font=('Segoe UI', 10))

        # Tant que les tokens n'existent pas alors ouvrir fenêtre de connexion
        if not token_manager.user_token_exist():
            logger.warning("User token does not exist !")
            try:
                app_key, app_secret = token_manager.get_app_tokens()
            except TypeError as e:
                logger.error("Impossible de trouver les tokens de l'application ! " + str(e))
                messagebox.showerror(
                    "Erreur",
                    "Impossible de trouver les tokens de l'application !"
                )
                self.exist = False
                self.parent.destroy()
                return
            connectemp = ITwython.ConnecTemporaire(app_key, app_secret)
            auth_url = connectemp.auth_url

            auth_window = auth_gui.FenetreConnexion(self, connectemp, auth_url)
            auth_window.grab_set()
            principal.wait_window(auth_window)

        # On récupère les différents tokens
        # On est normalement assuré des 4 éléments donc on peux utiliser l'unpacking
        # http://python-guide-pt-br.readthedocs.io/en/latest/writing/style/#unpacking
        self.app_key, self.app_secret, self.user_key, self.user_secret = token_manager.get_all_tokens()
        # Une fois qu'on a les tokens, créer la connexion

        self.connec = ITwython.Connec(self.app_key, self.app_secret, self.user_key, self.user_secret)

        if self.connec.exist:
            self.ajout_widget()
        else:
            messagebox.showerror(
                "Erreur",
                "Impossible de se connecter à Twitter !  Vérifiez vos paramètres réseaux et réessayez."
            )
            self.exist = False
            self.parent.destroy()
            return

    def ajout_widget(self):
        self.sidebar = Sidebar(self)
        self.sidebar.grid(column=0, row=0, sticky="nse")
        # self.sidebar.grid_propagate(0)

        self.cadre_tweet = EnvoiTweet(self)
        self.cadre_tweet.grid(column=1, row=0)

        self.tl = TimeLine(self, stream_connection=self.stream_connection, static_connection=self.static_connection)
        self.tl.grid(column=2, row=0)


class EnvoiTweet(Frame):
    """Définit le cadre avec les widgets pour envoyer un tweet, ainsi que les fonctions pour répondre aux actions des
    boutons des widgets nécessaires (bouton envoyer...)"""

    def __init__(self, parent, static_connection=True):
        logger.debug("Initialisation cadre : envoi de tweet")
        Frame.__init__(self, parent)
        self.parent = parent

        self.static_connection = static_connection

        if static_connection:
            self.connec = parent.connec
        else:
            self.connec = None

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
        if not self.static_connection:
            def action_async():
                logger.info("Entering action")

                # On dés
                # active l'entrée utilisateur pendant l'envoi du tweet
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


class Sidebar(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.configure(style="Sidebar.TFrame", width=80)

        self.cadre = Frame(self)
        self.cadre.grid(column=0, row=0, pady=20, padx=20)
        # Icones :
        # On utilise le code hexadécimal obtenu ici
        # https://docs.microsoft.com/en-us/uwp/api/Windows.UI.Xaml.Controls.Symbol
        self.icone_option = Label(self.cadre, text=chr(int("E115", 16)), font=('Segoe MDL2 Assets', 20),
                                  style="Sidebar.TLabel")
        self.icone_option.grid(row=0, column=0, sticky="s")


class TweetGUI(Frame):
    """Cadre pour afficher un tweet unique."""

    def __init__(self, parent, tweet: Tweet):
        logger.debug("Initialisation cadre : tweet")
        Frame.__init__(self, parent)
        self.parent = parent
        # self.connec = parent.connec

        # On met en place le cadre du tweet
        self.tweet = tweet

        screen_name = self.tweet.user.screen_name.encode("utf-8").decode('utf-8')
        name = self.tweet.user.name.encode("utf-8").decode('utf-8')
        status = self.tweet.text.encode("utf-8").decode('utf-8')
        date = self.tweet.created_at.encode("utf-8").decode('utf-8')

        # self.profile_image = Label(self, image=None)
        try:
            self.status = Message(self, text=status, width=380, foreground="white", background="#343232",
                                  font=('Segoe UI', 10))
        except tk.TclError as e:
            self.status = Message(self, text=status.encode("utf-8"), width=380, foreground="white",
                                  background="#343232", font=('Segoe UI', 10))
            logger.debug(e)

        try:
            self.name = Label(self, text=name)
        except tk.TclError as e:
            logger.debug(e)
            self.name = Label(self, text=name.encode("utf-8"))

        try:
            self.screen_name = Label(self, text="@" + screen_name)
        except tk.TclError as e:
            logger.debug(e)

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
    def __init__(self, parent, stream_connection=True, static_connection=True):
        logger.debug("Initialisation cadre : timeline")
        Frame.__init__(self, parent)
        self.parent = parent

        self.online = stream_connection

        # J'ai mis le canvas en bleu pour bien voir là où il est : on est pas censé le voir mais juste le frame
        # On utilise un frame dans un canvas car pas de scrollbar sur le frame => scrollbar sur canvas
        self.canvas = Canvas(self, borderwidth=0, width=400, background="blue")
        self.frame = Frame(self.canvas)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.grid(column=1, row=0, sticky="nes")
        self.canvas.grid(column=0, row=0, sticky="nesw")
        self.canvas.create_window((4, 4), window=self.frame,
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.config_cadre)

        self.ligne = 0

        if static_connection:
            tweets_data = self.parent.connec.get_home_timeline(count=50)
            # Example de réponse dans dev_assets/list_tweets

            # logger.debug(str(tweets_data).encode("utf-8"))
            for tweet in tweets_data:
                self.add_data(tweet)

        if stream_connection:
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
        if not static_connection and not stream_connection:
            self.peupler()

    def peupler(self):
        """Ajoute de fausses données pour travailler sur la mise en page hors-ligne,"
        " pour empecher de se faire bloquer par Twitter à force de recréer des connexions."""
        try:
            from dev_assets import list_tweets
            liste = list_tweets.list

            # On ajoute les données normalement
            for fake_tweet in liste:
                self.add_data(fake_tweet)
        except ImportError as e:
            logger.error("Can't import tweets ! " + str(e))

    def add_data(self, data):
        """Ajoute un objet TweetGUI à la TimeLine à partir de données brutes."""
        if 'text' in data:
            tweet = TweetGUI(self.frame, Tweet(data))
            tweet.grid(row=self.ligne, column=0)
            logger.debug(self.ligne)
            self.ligne = self.ligne + 1
            # self.scrollbar.grid_configure(rowspan=self.ligne + 1)

    def add_tweet(self, tweet: TweetGUI):
        tweet.grid(row=self.ligne, column=0)
        logger.debug(self.ligne)
        self.ligne = self.ligne + 1

    def config_cadre(self, event):
        """Reset the scroll region to encompass the inner frame."""
        logger.debug(event)
        logger.debug("OnFrameConfigurate.")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


# On commence le code ici
if __name__ == "__main__":
    logger.info("Starting Twysn")

    # Principal est la racine de l'app
    principal = tk.Tk()
    principal.title("TwISN")
    principal.config(bg='white')

    # on ne travaille pas directement dans principal
    # mais on utilise un cadre (Objet App)
    app = App(principal, stream_connection=False, static_connection=True)

    # On vérifie que l'application n'a pas été supprimée avec une erreur
    if app.exist:
        app.grid(sticky="nsew")
    principal.mainloop()
    logger.info("TWISN CLOSED")
