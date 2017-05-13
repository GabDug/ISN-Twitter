import os
import sys
import threading
import tkinter as tk
import urllib
from tkinter import messagebox
from tkinter.ttk import *
from urllib.request import urlopen

from PIL import Image, ImageTk

import ITwython
import auth_gui
import logger_conf
import path_finder
import token_manager
from ITwython import Tweet
from lib import mttkinter as tk

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
    def __init__(self, parent, stream_connection=True, static_connection=True, frozen=False):
        """stream_connection et static_connection permettent d'activer ou de désactiver les deux types de connection
         pour travailler ur la mise en page sans se faire bloquer par les limitations."""
        # On définit le cadre dans l'objet App (inutile car pas kwargs**...)
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.lift()

        self.exist = True

        self.frozen = frozen
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
            if self.connec.erreur == "token_invalid":
                messagebox.showwarning(
                    "Impossible de se connecter à Twitter !",
                    "Les identifiants de connexion sont invalides ou expirés, "
                    "merci de réessayer."
                )
                token_manager.delete_tokens()
            else:
                messagebox.showerror(
                    "Impossible de se connecter à Twitter !",
                    "Vérifiez vos paramètres réseaux et réessayez."
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

        self.sidebar.grid_propagate(0)
        self.sidebar.rowconfigure(0, weight=1)


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

        # On crée un cadre pour ajouter une marge égale
        self.cadre = Frame(self)
        self.cadre.grid(column=0, row=0, pady=10, padx=10)

        # On met en place le cadre d'envoi de tweet
        self.tweet_message = tk.StringVar()
        self.message_resultat = tk.StringVar()

        # TODO Utiliser un champ Text de plusieurs lignes
        self.label = Label(self.cadre, text="Nouveau tweet :")
        self.tweet = Entry(self.cadre, textvariable=self.tweet_message)
        self.bouton = Button(self.cadre, text="Tweeter", command=self.tweeter)
        self.message = Label(self.cadre, textvariable=self.message_resultat)

        self.label.grid(column=0, row=0)
        self.tweet.grid(column=0, row=1)
        self.bouton.grid(column=0, row=2)
        self.message.grid(column=0, row=3)

    def tweeter(self):
        # On récupère le message depuis le widget d'entrée de label
        message = self.tweet_message.get()

        # Si la connection est activé (pas debug)
        if self.static_connection:
            def action_async():
                logger.debug("Tweet : Début action_async")

                # On désactive l'entrée utilisateur pendant l'envoi du tweet
                self.tweet.state(["disabled"])
                self.bouton.state(["disabled"])

                # On lance le tweet via ITwython
                succes, msg = self.connec.tweeter(message)

                logger.debug("Tweet : Succès : " + str(succes))
                logger.debug("Tweet : Message : " + str(msg))

                # On lance les actions de retour
                self.callback(succes, msg)
                logger.debug("Tweet : Fin action_async")
                return

            # On lance l'action du tweet dans un thread asynchrone
            th = threading.Thread(target=action_async, daemon=True)
            th.start()

    def callback(self, succes: bool, msg_):
        """Éxecuté après l'envoi du tweet, pour afficher un message de confirmation ou d'erreur."""
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


class Sidebar(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.configure(style="Sidebar.TFrame", width=80)

        self.cadre = Frame(self)
        self.cadre.grid(column=0, row=0, pady=20, padx=20, sticky="s")

        # Icones :
        # On utilise le code hexadécimal obtenu ici
        # https://docs.microsoft.com/en-us/uwp/api/Windows.UI.Xaml.Controls.Symbol
        self.icone_utilisateur = Label(self.cadre, text=chr(int("E13D", 16)), font=('Segoe MDL2 Assets', 20),
                                       style="Sidebar.TLabel")
        self.icone_option = Label(self.cadre, anchor=tk.S, text=chr(int("E115", 16)), font=('Segoe MDL2 Assets', 20),
                                  style="Sidebar.TLabel")

        self.icone_utilisateur.grid(row=0, column=0, sticky="s", ipady=20)
        self.icone_option.grid(row=1, column=0, sticky="s")

        self.cadre.grid_columnconfigure(0, weight=3)

'''
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
            self.status = tk.Message(self, text=status, width=380, foreground="white", background="#343232",
                                     font=('Segoe UI', 10))
        except tk.TclError as e:
            self.status = tk.Message(self, text=status.encode("utf-8"), width=380, foreground="white",
                                     background="#343232", font=('Segoe UI', 10))
            logger.error(e)

        try:
            self.name = Label(self, text=name)
        except tk.TclError as e:
            logger.error(e)
            self.name = Label(self, text=name.encode("utf-8"))

        try:
            self.screen_name = Label(self, text="@" + screen_name)
        except tk.TclError as e:
            logger.error(e)

        self.date = Label(self, text=date)

        self.profile_picture = ProfilePictureGUI(self, self.tweet)
        # self.fav_count = Label(self, text="0")
        # self.rt_count = Label(self, text="1")

        self.profile_picture.pack()
        self.name.pack()
        self.screen_name.pack()
        self.status.pack()
        self.date.pack()
        # self.fav_count.pack()
        # self.rt_count.pack()
'''

class TweetGUI(Frame):
    """Cadre pour afficher un tweet unique."""

    def __init__(self, parent, tweet: Tweet):
        logger.debug("Initialisation cadre : tweet")
        Frame.__init__(self, parent)

        style = Style()
        style.configure("Test.TFrame", foreground="white", background="blue", font=('Segoe UI', 10))
        style.configure("TLabel", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TFrame", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TEntry", foreground="red", background="#343232", font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 10))

        style.configure("Sidebar.TFrame", foreground="white", background="#111111", font=('Segoe UI', 10))
        style.configure("Sidebar.TLabel", foreground="white", background="#111111", font=('Segoe UI', 10))

        self.parent = parent
        # self.connec = parent.connec
        self.tweet = tweet
        # On met en place le cadre du tweet

        screen_name = self.tweet.user.screen_name.encode("utf-8").decode('utf-8')
        name = self.tweet.user.name.encode("utf-8").decode('utf-8')
        #TODO mettre une limite de caractere ? (pour ne pas avoir de probleme avec laffichage
        status = self.tweet.text.encode("utf-8").decode('utf-8')
        date = self.tweet.created_at.encode("utf-8").decode('utf-8')

        # self.profile_image = Label(self, image=None)
        try:
            self.status = tk.Message(self, text=status, width=320, foreground="white", background="#343232",
                                     font=('Segoe UI', 10))
        except tk.TclError as e:
            self.status = tk.Message(self, text=status.encode("utf-8"), width=380, foreground="white",
                                     background="#343232", font=('Segoe UI', 10))

        try:
            self.name = Label(self, text=name)
        except tk.TclError as e:
            self.name = Label(self, text=name.encode("utf-8"))

        try:
            self.screen_name = Label(self, text="@" + screen_name)
        except tk.TclError as e:
            pass

        self.date = Label(self, text=date)

        self.lien = "https://pbs.twimg.com/profile_images/817042499134980096/LTpqSDMM_bigger.jpg"
        save_relatif = self.lien.replace(":", "").replace("/", "")
        cache_dir = ""
        # On crée un string avec le lien absolu vers le fichier
        self.save = save_relatif

        if os.path.isfile(self.save):
            print("File already exists ! ")
        # Sinon on le télécharge
        else:

            try:
                testfile = urllib.request.URLopener()
                testfile.retrieve(self.lien, self.save)
                # aa = "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"
                # internal data file
                # data_stream = io.BytesIO(aa)
                # open as a PIL image object

            except urllib.error.HTTPError as e:
                print("HTTP ERROR PROFILE PICTURE !" + str(e))
                return

        Cadre1 = Frame(self, cursor='dot', width=500, height=50, style="TLabel")
        Cadre1.grid(column=0, row=5, columnspan=5, padx=0, pady=0, sticky='')

        cadre2 = Frame(self, cursor='arrow', width=100, height=100, style="Test.TFrame")
        cadre2.grid(column=0, row=0, rowspan=2, padx=20, pady=20, sticky='N')

        separateur = Frame(self, width=500, height=8)
        separateur.grid(column=0, row=6, columnspan=5)

        # self.profile_picture = ProfilePictureGUI(self)
        self.image = Image.open(self.save)
        self.profile_picture = ImageTk.PhotoImage(self.image)
        image = Label(self, image=self.profile_picture)

        self.likes_count = Label(self, text="                 ")
        self.fav_count = Label(self, text="              : 1")
        self.icone_fav_off = Label(Cadre1, text=chr(int("E1CE", 16)), font=('Segoe MDL2 Assets', 20), style="TLabel")
        self.icone_fav_on = Label(Cadre1, text=chr(int("E1CF", 16)), font=('Segoe MDL2 Assets', 20), style="TLabel")
        self.rt_count = Label(self, text="            : 1")
        # self.icone_like_off = Label(self,text=chr(int("E19F", 16)), font=('Segoe MDL2 Assets', 20), style="Sidebar.TLabel")
        # self.icone_like_on = Label(self, text=chr(int("E19E", 16)), font=('Segoe MDL2 Assets', 20), style="Sidebar.TLabel")
        self.icone_rt_off = Label(Cadre1, text=chr(int("E1CA", 16)), font=('Segoe MDL2 Assets', 20), style="TLabel")
        self.icone_rt_on = Label(Cadre1, text=chr(int("E10E", 16)), font=('Segoe MDL2 Assets', 20), style="TLabel")
        self.icone_reply = Label(Cadre1, text=chr(int("E15F", 16)), font=('Segoe MDL2 Assets', 20), style="TLabel")
        # self.name = Label(self, text='Gabigabigoooo')
        # self.screen_name = Label(self, text='@DUGNYCHON_DIVIN')

        # GRID
        image.grid(column=0, row=0, pady=30, rowspan=2, sticky='N')
        self.name.grid(column=1, row=0, pady=15, sticky='N')
        self.screen_name.grid(column=2, row=0, pady=0)
        self.status.grid(column=1, row=1, columnspan=3, sticky='NE')
        self.date.grid(column=3, row=2, pady=15, sticky='E')

        self.icone_reply.grid(column=1, row=0, pady=2, padx=30, sticky="W")
        # self.likes_count.grid(column=1, row=5, pady=2)


        # self.fav_count.grid(column=2, row=5, pady=2)
        self.icone_fav_off.grid(column=2, row=0, pady=2, padx=30)
        # self.icone_fav_on.grid(column=2, row=5, pady=2)

        # self.rt_count.grid(column=3, row=5, pady=2)
        self.icone_rt_off.grid(column=3, row=0, pady=2, padx=30)

        # self.icone_rt_on.grid(column=3, row=5, pady=2)


        # Fonctions
        # TODO récuperer tweet_id

        def fav(event):
            print('fav')
            # twitter.create_favorite(id = tweet_id)
            self.parent.parent.connec.fav(message)
            self.icone_fav_on.grid(column=2, row=0, pady=2, padx=30)

        def defav(event):
            print('defav')
            self.parent.parent.connec.defav(message)
            self.icone_fav_on.grid_forget()

        def rt_on(event):
            print("retweet")
            # twitter.retweet(id = tweet["id_str"])
            self.parent.parent.connec.retweet(message)
            self.icone_rt_on.grid(column=3, row=0, pady=2, padx=30)

        def rt_off(event):
            print("annule retweet")
            # annuler le retweet
            self.parent.parent.connec.unretweet(message)
            self.icone_rt_on.grid_forget()

        def reply(event):
            print("reply")
            # TODO fonction pour ouvrir fenêtre de réponse à 1 utilisateur
            self.icone_reply['state'] = "disabled"


        #BINDING
        self.icone_fav_off.bind("<Button-1>", fav)
        self.icone_fav_on.bind("<Button-1>", defav)
        self.icone_rt_on.bind("<Button-1>", rt_off)
        self.icone_rt_off.bind("<Button-1>", rt_on)
        # self.icone_like_off.bind("<Button-1>", like)
        # self.icone_like_on.bind("<Button-1>", dislike)
        self.icone_reply.bind("<Button-1>", reply)



class ProfilePictureGUI(Frame):
    def __init__(self, parent, tweet: Tweet):
        logger.debug("Initialisation cadre : photo de profil")
        Frame.__init__(self, parent)

        self.lien = tweet.user.profile_image_url

        # TODO Fixer le lien si l'app est frozen
        # On supprime les : et / de l'url pour en faire un nom de fichier
        save_relatif = self.lien.replace("http://", "").replace("https://", "").replace(":", "").replace("/", ".")
        # On obtient le répertoire de sauvegarde des photos
        cache_dir = path_finder.PathFinder.get_cache_directory()
        logger.debug("Dossier cache : " + cache_dir)

        # On crée un string avec le lien absolu vers le fichier
        self.save = save_relatif
        logger.debug("Fichier cache : " + self.save)

        # Si le fichier n'existe pas alors on le télécharge
        if not os.path.isfile(self.save):
            logger.debug("Téléchargement du fichier.")
            try:
                testfile = urllib.request.URLopener()
                testfile.retrieve(self.lien, self.save)
                # aa = "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"
                # internal data file
                # data_stream = io.BytesIO(aa)
                # open as a PIL image object

            except urllib.error.HTTPError as e:
                logger.error("HTTP ERROR PROFILE PICTURE !" + str(e))
                return

        # TODO Ajouter exception pour ouverture fichier
        self.pil_image = Image.open(self.save)
        self.photo = ImageTk.PhotoImage(self.pil_image)

        label = Label(self, image=self.photo)
        label.pack(padx=5, pady=5)


class TimeLine(Frame):
    def __init__(self, parent, stream_connection=True, static_connection=True):
        logger.debug("Initialisation cadre : timeline")
        Frame.__init__(self, parent)
        self.parent = parent

        self.online = stream_connection

        # J'ai mis le canvas en bleu pour bien voir là où il est : on est pas censé le voir mais juste le frame
        # On utilise un frame dans un canvas car pas de scrollbar sur le frame => scrollbar sur canvas
        self.canvas = tk.Canvas(self, borderwidth=0, width=400, background="blue")
        self.frame = Frame(self.canvas)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.grid(column=1, row=0, sticky="nes")
        self.canvas.grid(column=0, row=0, sticky="nesw")
        self.canvas.create_window((0, 0), window=self.frame,
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
                # Sinon on doit modifier le fichier helper de la librairie twython => hack peu pratique
                # On utilise un unpacking avec double splat http://deusyss.developpez.com/tutoriels/Python/args_kwargs/
                self.streamer.user(**{"with": "followings"})
                return
                # TODO voir si ça marche le return

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
            if self.parent.frozen:
                import list_tweets
            else:
                from dev_assets import list_tweets
            liste = list_tweets.list

            # On ajoute les données normalement
            for fake_tweet in liste:
                self.add_data(fake_tweet)
        except ImportError as e:
            logger.error("Impossible d'importer le stock de tweets ! " + str(e))

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
        # TODO Bloquer scroll à la fin
        logger.debug("Reconfiguration Cadre TimeLine : " + str(event))
        logger.debug(self.scrollbar.get())
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        logger.debug(self.scrollbar.get())

'''
# On commence le code ici
if __name__ == "__main__":
    logger.info("Démarrage de TwISN")

    # Principal est la racine de l'app
    principal = tk.Tk()
    principal.title("TwISN")
    principal.config(bg='white')

    # Récupération du chemin de l'icone et de l'état de l'applciation:
    frozen, chemin_absolu = path_finder.PathFinder.get_icon_path()

    # On charge l'icone
    icon = tk.PhotoImage(file=chemin_absolu)
    # Ajoutée dans le gestionnaire de fenêtre Windows
    principal.tk.call('wm', 'iconphoto', principal._w, icon)

    # On ne travaille pas directement dans principal (objet Tk)
    # Mais on utilise un cadre (Objet App qui hérite de Frame)
    # stream_connection et static_connnection sont utilisées pour bloquer les connexions
    # pendant le développement de l'application
    app = App(principal, stream_connection=False, static_connection=True, frozen=frozen)

    # On vérifie que l'application n'a pas été supprimée avec une erreur
    if app.exist:
        app.grid(sticky="nsew")
        app.columnconfigure(1, weight=1)
        app.rowconfigure(0, weight=1)

    principal.mainloop()
    app.quit()
    principal.quit()
    logger.info("Fermeture de TwISN")
    sys.exit()
'''
if __name__ == '__main__':
    t = tk.Tk()
    data = {'created_at': 'Sun Apr 16 20:05:02 +0000 2017', 'id': 853700783006773250, 'id_str': '853700783006773250',
         'text': 'RT @Wale: I just met Lauryn Hill and hugged SZA in a 5 min span... Coachella is officially Disney land 😊',
         'truncated': False, 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [
            {'screen_name': 'Wale', 'name': 'Wale', 'id': 17929027, 'id_str': '17929027', 'indices': [3, 8]}],
                                          'urls': []},
         'source': '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>',
         'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None, 'in_reply_to_user_id': None,
         'in_reply_to_user_id_str': None, 'in_reply_to_screen_name': None,
         'user': {'id': 1380046638, 'id_str': '1380046638', 'name': 'pat', 'screen_name': 'shonenmami',
                  'location': 'Cosa nostra', 'description': '*special snowflake *', 'url': 'https://t.co/IwQdYm1nV1',
                  'entities': {'url': {'urls': [
                      {'url': 'https://t.co/IwQdYm1nV1', 'expanded_url': 'https://youtu.be/Fof9lHaApXc',
                       'display_url': 'youtu.be/Fof9lHaApXc', 'indices': [0, 23]}]}, 'description': {'urls': []}},
                  'protected': False, 'followers_count': 983, 'friends_count': 342, 'listed_count': 40,
                  'created_at': 'Thu Apr 25 18:06:31 +0000 2013', 'favourites_count': 1663, 'utc_offset': 7200,
                  'time_zone': 'Paris', 'geo_enabled': True, 'verified': False, 'statuses_count': 91238, 'lang': 'fr',
                  'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False,
                  'profile_background_color': 'C0DEED',
                  'profile_background_image_url': 'http://pbs.twimg.com/profile_background_images/468122332091781120/UwUDLKHD.jpeg',
                  'profile_background_image_url_https': 'https://pbs.twimg.com/profile_background_images/468122332091781120/UwUDLKHD.jpeg',
                  'profile_background_tile': True,
                  'profile_image_url': 'http://pbs.twimg.com/profile_images/852948354673905664/uJtKgIjB_normal.jpg',
                  'profile_image_url_https': 'https://pbs.twimg.com/profile_images/852948354673905664/uJtKgIjB_normal.jpg',
                  'profile_banner_url': 'https://pbs.twimg.com/profile_banners/1380046638/1492131018',
                  'profile_link_color': '1B95E0', 'profile_sidebar_border_color': 'FFFFFF',
                  'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333',
                  'profile_use_background_image': True, 'has_extended_profile': True, 'default_profile': False,
                  'default_profile_image': False, 'following': True, 'follow_request_sent': False,
                  'notifications': False, 'translator_type': 'regular'}, 'geo': None, 'coordinates': None,
         'place': None, 'contributors': None,
         'retweeted_status': {'created_at': 'Sun Apr 16 06:53:17 +0000 2017', 'id': 853501532511158272,
                              'id_str': '853501532511158272',
                              'text': 'I just met Lauryn Hill and hugged SZA in a 5 min span... Coachella is officially Disney land 😊',
                              'truncated': False,
                              'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []},
                              'source': '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>',
                              'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None,
                              'in_reply_to_user_id': None, 'in_reply_to_user_id_str': None,
                              'in_reply_to_screen_name': None,
                              'user': {'id': 17929027, 'id_str': '17929027', 'name': 'Wale', 'screen_name': 'Wale',
                                       'location': '', 'description': 'S H i N E', 'url': 'https://t.co/C9z5FuktdG',
                                       'entities': {'url': {'urls': [{'url': 'https://t.co/C9z5FuktdG',
                                                                      'expanded_url': 'https://atlanti.cr/preordershine',
                                                                      'display_url': 'atlanti.cr/preordershine',
                                                                      'indices': [0, 23]}]},
                                                    'description': {'urls': []}}, 'protected': False,
                                       'followers_count': 5371582, 'friends_count': 2439, 'listed_count': 12470,
                                       'created_at': 'Sat Dec 06 21:15:10 +0000 2008', 'favourites_count': 1542,
                                       'utc_offset': -18000, 'time_zone': 'Central Time (US & Canada)',
                                       'geo_enabled': True, 'verified': True, 'statuses_count': 63687, 'lang': 'en',
                                       'contributors_enabled': False, 'is_translator': False,
                                       'is_translation_enabled': True, 'profile_background_color': '000000',
                                       'profile_background_image_url': 'http://pbs.twimg.com/profile_background_images/378800000013969591/12be27ae8ce2ec071a2b6126c308ea5e.png',
                                       'profile_background_image_url_https': 'https://pbs.twimg.com/profile_background_images/378800000013969591/12be27ae8ce2ec071a2b6126c308ea5e.png',
                                       'profile_background_tile': False,
                                       'profile_image_url': 'http://pbs.twimg.com/profile_images/843521441211604993/QuyIRC7f_normal.jpg',
                                       'profile_image_url_https': 'https://pbs.twimg.com/profile_images/843521441211604993/QuyIRC7f_normal.jpg',
                                       'profile_link_color': '1B95E0', 'profile_sidebar_border_color': 'FFFFFF',
                                       'profile_sidebar_fill_color': 'FFFFFF', 'profile_text_color': '000000',
                                       'profile_use_background_image': False, 'has_extended_profile': False,
                                       'default_profile': False, 'default_profile_image': False, 'following': False,
                                       'follow_request_sent': False, 'notifications': False, 'translator_type': 'none'},
                              'geo': None, 'coordinates': None, 'place': None, 'contributors': None,
                              'is_quote_status': False, 'retweet_count': 2596, 'favorite_count': 7487,
                              'favorited': False, 'retweeted': False, 'lang': 'en'}, 'is_quote_status': False,
         'retweet_count': 2596, 'favorite_count': 0, 'favorited': False, 'retweeted': False, 'lang': 'en'}
    tweet = Tweet(data)
    tweeti = TweetGUI(t, tweet)
    tweeti.pack()
    t.mainloop()