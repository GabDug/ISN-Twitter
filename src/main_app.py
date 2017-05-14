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
import options_gui
import path_finder
import token_manager
import user_gui
from ITwython import Tweet

try:
    from lib import mttkinter as tk
except:
    import mttkinter as tk

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
        style.configure("Test.TFrame", foreground="black", background="green", font=('Segoe UI', 10))
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

        if token_manager.app_token_exist():
            self.connec = ITwython.Connec(self.app_key, self.app_secret, self.user_key, self.user_secret)
            erreur = self.connec.erreur
        else:
            erreur = "no_app_tokens"
            self.connec = None

        if not (self.connec is None) and self.connec.exist:
            self.ajout_widget()
        else:
            if erreur == "token_invalid":
                messagebox.showwarning(
                    "Impossible de se connecter à Twitter !",
                    "Les identifiants de connexion sont invalides ou expirés, "
                    "merci de réessayer."
                )
                token_manager.delete_tokens()
            elif erreur == "app_token_invalid":
                messagebox.showerror(
                    "Impossible de se connecter à Twitter !",
                    "Les jetons de l'application sont invalides ou expirés, "
                    "merci de mettre l'application à jour."
                )
            elif erreur == "no_app_tokens":
                messagebox.showerror(
                    "Impossible de se connecter à Twitter !",
                    "Vérifiez la présence du fichier data/app_tokens !"
                )
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
        self.sidebar.grid_propagate(0)
        self.sidebar.rowconfigure(0, weight=1)

        self.cadre_tweet = EnvoiTweet(self)
        self.cadre_tweet.grid(column=1, row=0)

        self.tl = TimeLine(self, stream_connection=self.stream_connection, static_connection=self.static_connection)
        self.tl.grid(column=2, row=0)
        self.tl.columnconfigure(2, weight=1)
        self.tl.rowconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)


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
        self.parent = parent
        self.configure(style="Sidebar.TFrame", width=80)

        self.cadre = Frame(self)
        self.cadre.grid(column=0, row=0, pady=20, padx=20, sticky="s")

        # Icones :
        # On utilise le code hexadécimal obtenu ici
        # https://docs.microsoft.com/en-us/uwp/api/Windows.UI.Xaml.Controls.Symbol
        self.icone_utilisateur = Label(self.cadre, text=chr(int("E13D", 16)), font=('Segoe MDL2 Assets', 20),
                                       style="Sidebar.TLabel")
        self.icone_utilisateur.bind("<Button-1>", lambda __: self.clic_utilisateur())
        self.icone_option = Label(self.cadre, anchor=tk.S, text=chr(int("E115", 16)), font=('Segoe MDL2 Assets', 20),
                                  style="Sidebar.TLabel")
        self.icone_option.bind("<Button-1>", lambda __: self.clic_options())

        self.icone_utilisateur.grid(row=0, column=0, sticky="s", ipady=20)
        self.icone_option.grid(row=1, column=0, sticky="s")

        self.cadre.grid_columnconfigure(0, weight=3)

    def clic_options(self):
        logger.debug("Clic options")
        fenetre_options = options_gui.FenetreOptions(self, self.parent.connec.user)
        fenetre_options.grab_set()
        principal.wait_window(fenetre_options)

    def clic_utilisateur(self):
        logger.debug("Clic utilisateur")
        fenetre_utilisateur = user_gui.FenetreUtilisateur(self, self.parent.connec.user)
        fenetre_utilisateur.grab_set()
        principal.wait_window(fenetre_utilisateur)


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

    def __init__(self, parent, tweet: Tweet, timeline):
        logger.debug("Initialisation cadre : TweetGUI")
        Frame.__init__(self, parent)
        self.parent = parent
        self.timeline = timeline
        self.tweet = tweet

        style = Style()
        style.configure("Test.TFrame", foreground="white", background="red", font=('Segoe UI', 10))
        style.configure("TLabel", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TFrame", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TEntry", foreground="red", background="#343232", font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 10))

        style.configure("Sidebar.TFrame", foreground="white", background="#111111", font=('Segoe UI', 10))
        style.configure("Sidebar.TLabel", foreground="white", background="#111111", font=('Segoe UI', 10))

        self.id = tweet.id
        screen_name = self.tweet.user.screen_name.encode("utf-8").decode('utf-8')
        name = self.tweet.user.name.encode("utf-8").decode('utf-8')
        # TODO mettre une limite de caractere ? (pour ne pas avoir de probleme avec l'affichage)
        status = self.tweet.text.encode("utf-8").decode('utf-8')
        date = self.tweet.created_at.encode("utf-8").decode('utf-8')

        try:
            self.status = tk.Message(self, text=status, width=480, foreground="white", background="#343232",
                                     font=('Segoe UI', 10))
        except tk.TclError as e:
            self.status = tk.Message(self, text=status.encode("utf-8"), width=480, foreground="white",
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

        # cadre2 = Frame(self, cursor='arrow', width=100, height=100, style="Test.TFrame")
        # cadre2.grid(column=0, row=0, rowspan=2, padx=20, pady=20, sticky='N')

        separateur = Frame(self, width=500, height=8)
        separateur.grid(column=0, row=6, columnspan=5)

        self.profile_picture = ProfilePictureGUI(self, self.tweet, cache_dir=self.timeline.cache_dir)

        cadre_actions = Frame(self, cursor='dot', width=500, height=50, style="TLabel")
        # TODO Mdr c'est quoi ça ? text="                 " sérieusement ?
        self.fav_count = Label(self, text="              : 1")

        self.fav_variable = tk.StringVar()
        if not tweet.favorited:
            self.fav_variable.set(chr(int("E1CE", 16)))
        else:
            self.fav_variable.set(chr(int("E1CF", 16)))
        self.icone_fav = Label(cadre_actions, textvariable=self.fav_variable, font=('Segoe MDL2 Assets', 14),
                               style="TLabel")

        self.rt_count = Label(self, text="            : 1")
        self.icone_rt = Label(cadre_actions, text=chr(int("E1CA", 16)), font=('Segoe MDL2 Assets', 14),
                              style="TLabel")
        # chr(int("E10E", 16))

        self.icone_reply = Label(cadre_actions, text=chr(int("E15F", 16)), font=('Segoe MDL2 Assets', 14),
                                 style="TLabel")

        self.profile_picture.grid(column=0, row=0, pady=0, rowspan=1, sticky='NW')
        self.name.grid(column=1, row=0, pady=0, sticky='S')
        self.screen_name.grid(column=2, row=0, sticky='S', pady=0)
        self.status.grid(column=1, row=1, columnspan=2, sticky='NW')
        self.date.grid(column=1, columnspan=2, row=2, pady=0, sticky='E')

        cadre_actions.grid(column=0, row=3, columnspan=3, padx=0, pady=0, sticky='E')

        self.icone_reply.grid(column=0, row=0, pady=2, padx=00, sticky="")
        # self.likes_count.grid(column=1, row=5, pady=2)

        # self.fav_count.grid(column=2, row=5, pady=2)
        self.icone_fav.grid(column=1, row=0, pady=2, padx=00, sticky="E")
        # self.icone_fav_on.grid(column=2, row=5, pady=2)

        # self.rt_count.grid(column=3, row=5, pady=2)
        self.icone_rt.grid(column=2, row=0, pady=2, padx=00, sticky="E")

        def clic_fav(event):
            logger.debug('Clic fav : ' + self.id)
            self.timeline.parent.connec.fav(self.id)
            self.fav_variable.set(chr(int("E1CF", 16)))
            # On ne change pas de Label, on change juste le texte

        def clic_rt(event):
            logger.debug('Clic RT : ' + self.id)
            self.timeline.parent.connec.retweet(self.id)
            # self.icone_rt_on.grid(column=3, row=0, pady=2, padx=30)

        # def rt_off(event):
        #     print("annule retweet")
        #     # annuler le retweet
        #     self.timeline.parent.connec.unretweet(self.id)
        #     self.icone_rt_on.grid_forget()

        def clic_reply(event):
            logger.debug('Clic reply : ' + self.id)
            # TODO fonction pour ouvrir fenêtre de réponse à 1 utilisateur
            self.icone_reply['state'] = "disabled"

        # BINDING
        self.icone_fav.bind("<Button-1>", clic_fav)
        self.icone_rt.bind("<Button-1>", clic_rt)
        self.icone_reply.bind("<Button-1>", clic_reply)


class ProfilePictureGUI(Frame):
    def __init__(self, parent, tweet: Tweet, cache_dir=path_finder.PathFinder.get_cache_directory()):
        logger.debug("Initialisation cadre : photo de profil")
        Frame.__init__(self, parent)

        self.lien = tweet.user.profile_image_url_normal

        # TODO Fixer le lien si l'app est frozen
        # On supprime les : et / de l'url pour en faire un nom de fichier
        save_relatif = self.lien.replace("http://", "").replace("https://", "").replace(":", "").replace("/", ".")

        # logger.debug("Dossier cache : " + cache_dir)

        # On crée un string avec le lien absolu vers le fichier
        self.save = cache_dir + "/" + save_relatif
        logger.debug("Fichier cache : " + self.save)

        def action_async():
            # Si le fichier n'existe pas alors on le télécharge
            if not os.path.isfile(self.save):
                logger.debug("Téléchargement du fichier : " + self.save)
                try:
                    testfile = urllib.request.URLopener()
                    testfile.retrieve(self.lien, self.save)

                except urllib.error.HTTPError as e:
                    logger.error("HTTP Error when downloading pp!" + str(e))
                    return

            # TODO Ajouter exception pour ouverture fichier
            self.pil_image = Image.open(self.save)
            self.photo = ImageTk.PhotoImage(self.pil_image)

            label = Label(self, image=self.photo)
            label.pack(padx=5, pady=5)

        thread_tl = threading.Thread(target=action_async, daemon=True)
        thread_tl.start()


class TimeLine(Frame):
    def __init__(self, parent, stream_connection=True, static_connection=True):
        logger.debug("Initialisation cadre : timeline")
        style = Style()
        style.configure("Test.TFrame", foreground="white", background="purple", font=('Segoe UI', 10))
        Frame.__init__(self, parent, style="Test.TFrame")
        self.parent = parent

        # On récupère le dossier de cache pour les photos
        self.cache_dir = path_finder.PathFinder.get_cache_directory()

        self.online = stream_connection

        # J'ai mis le canvas en bleu pour bien voir là où il est : on est pas censé le voir mais juste le frame
        # On utilise un frame dans un canvas car pas de scrollbar sur le frame => scrollbar sur canvas
        self.canvas = tk.Canvas(self, borderwidth=0, width=580, background="blue")
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

            print(tweets_data)
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
            tweet = TweetGUI(self.frame, Tweet(data), self)
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


# On commence le code ici
if __name__ == "__main__":
    logger.info("Démarrage de TwISN")

    # Principal est la racine de l'app
    principal = tk.Tk()
    principal.title("TwISN")
    principal.config(bg='pink')  # TODO remove debug
    principal.minsize(width=850, height=300)

    principal.columnconfigure(0, weight=1)
    principal.rowconfigure(0, weight=1)
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
    app = App(principal, stream_connection=True, static_connection=True, frozen=frozen)

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
