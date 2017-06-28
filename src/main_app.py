"""Twython, simple graphical Python Twitter client. 
Copyright (C) 2017  Quentin ANDRIEUX and Gabriel DUGNY

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

# -*- coding: utf-8 -*-
import os
import sys
import threading
import tkinter as tk
import urllib
# noinspection PyUnresolvedReferences
from multiprocessing import Queue
from tkinter import messagebox
from tkinter.ttk import *
from urllib.request import urlopen

# noinspection PyUnresolvedReferences
import requests
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
except ModuleNotFoundError:
    import mttkinter as tk

logger = logger_conf.Log.logger


# Structure d'après
# https://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application
# Classe qui hérite de Frame
class App(Frame):
    def __init__(self, parent, connexion_stream=True, connexion_statique=True, frozen=False):
        """Cadre principal. Contient les divers widgets ainsi que les attributs nécessaires à l'application.
        connexion_stream et connexion_statique permettent d'activer ou de désactiver les deux types de connexion
         pour travailler ur la mise en page sans se faire bloquer par les limitations."""
        # On définit le cadre dans l'objet App (inutile car pas kwargs**...)
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.lift()

        # Attribut utilisé pour montrer que tout va bien, False si doit ou va être détruit
        self.existe = True

        self.frozen = frozen
        self.stream_connection = connexion_stream
        self.static_connection = connexion_statique

        style = Style()
        style.configure("TLabel", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TFrame", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TEntry", foreground="black", background="#343232", font=('Segoe UI', 10))
        style.configure("Test.TFrame", foreground="black", background="#343232", font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 10))

        style.configure("Sidebar.TFrame", foreground="white", background="#111111", font=('Segoe UI', 10))
        style.configure("Sidebar.TLabel", foreground="white", background="#111111", font=('Segoe UI', 10))

        # Si les tokens n'existent pas alors ouvrir fenêtre de connexion
        if not token_manager.user_token_exist():
            logger.warning("Les tokens utilisateurs n'existent pas !")
            # On vérifie l'existence des tokens de l'application
            try:
                app_key, app_secret = token_manager.get_app_tokens()

            # S'ils nexistent pas on ferme App
            except TypeError as e:
                logger.error("Impossible de trouver les tokens de l'application ! " + str(e))
                messagebox.showerror(
                    "Erreur",
                    "Impossible de trouver les tokens de l'application !"
                )
                self.existe = False
                self.parent.destroy()
                return
            co_temporaire = ITwython.ConnexionTemporaire(app_key, app_secret)
            auth_url = co_temporaire.auth_url

            auth_window = auth_gui.FenetreConnexion(self, co_temporaire, auth_url)
            auth_window.grab_set()
            principal.wait_window(auth_window)

        # On récupère les différents tokens
        # On est normalement assuré des 4 éléments donc on peux utiliser l'unpacking
        # http://python-guide-pt-br.readthedocs.io/en/latest/writing/style/#unpacking
        self.app_key, self.app_secret, self.user_key, self.user_secret = token_manager.get_all_tokens()
        # Une fois qu'on a les tokens, créer la connexion

        if token_manager.app_token_exist():
            self.connexion = ITwython.Connexion(self.app_key, self.app_secret, self.user_key, self.user_secret)
            erreur = self.connexion.erreur
        else:
            erreur = "no_app_tokens"
            self.connexion = None

        # Si la connexion existe
        if not (self.connexion is None) and self.connexion.existe:
            # On ajoute les widgets
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
                # TODO Cas executé aussi si fermeture fenêtre auth_gui
                messagebox.showerror(
                    "Impossible de se connecter à Twitter !",
                    "Vérifiez vos paramètres réseaux et réessayez."
                )
            self.existe = False
            self.parent.destroy()
            return

    @staticmethod
    def final(fenetre, co_temporaire, code_pin):
        """Fonction qui sauvegarde les tokens définitifs avec le code PIN et la connexion temporaire."""
        succes, login_credentials = co_temporaire.final(code_pin)
        if succes:
            user_token, user_token_secret = login_credentials["oauth_token"], login_credentials["oauth_token_secret"]
            logger.debug("Oauth Token : {0}, Oauth Token Secret : {1}".format(user_token, user_token_secret))
            token_manager.set_tokens(user_token, user_token_secret)
            logger.debug(token_manager.get_all_tokens())
            fenetre.destroy()
        else:
            # Si succes == False alors login_credentials est un message d'erreur
            logger.error("Erreur fatale : " + login_credentials)


class EnvoiTweet(Frame):
    """Définit le cadre avec les widgets pour envoyer un tweet, ainsi que les fonctions pour répondre aux actions des
    boutons des widgets nécessaires (bouton envoyer...)"""

    def __init__(self, parent, connexion_statique=True):
        logger.debug("Initialisation cadre : envoi de tweet")
        Frame.__init__(self, parent)
        self.parent = parent

        self.connexion_statique = connexion_statique

        if connexion_statique:
            self.connexion = parent.connexion
        else:
            self.connexion = None

        self.id_reponse = None
        self.tweet_reponse = None

        # On crée un cadre pour ajouter une marge égale
        self.cadre = Frame(self)
        self.cadre.grid(column=0, row=0, pady=10, padx=10)

        # On met en place le cadre d'envoi de tweet
        self.message_resultat = tk.StringVar()

        # TODO Utiliser un champ Text de plusieurs lignes
        self.titre = Label(self.cadre, text="Écrire un nouveau Tweet")
        self.texte_tweet = tk.Text(self.cadre, width=30, height=6, wrap='word', font=('Segoe UI', 10))
        self.bouton = Button(self.cadre, text="Tweeter", command=self.tweeter)
        self.message = Label(self.cadre, textvariable=self.message_resultat)

        self.titre.grid(column=0, row=0)
        self.texte_tweet.grid(column=0, row=1)
        self.bouton.grid(column=0, row=2, pady=10)
        self.message.grid(column=0, row=3)

    def mode_reponse(self, tweet: Tweet):
        self.labelreponse = Label(self.cadre, text="Répondre à @" + tweet.user.screen_name)
        self.labelreponse.grid(column=0, row=4)
        self.id_reponse = tweet.id
        self.tweet_reponse = tweet

    def tweeter(self):
        '''Permet d'appeler la fonction tweeter de ITwython'''
        # On récupère le message depuis le widget d'entrée de label
        message = self.texte_tweet.get("1.0", 'end-1c')

        # Si la connexion est activé (pas debug)
        if self.connexion_statique and message != "":
            def action_async():
                logger.debug("Tweet : Début action_async")

                # On désactive le bouton pendant l'envoi du tweet
                # self.texte_tweet.configure(state="disabled")
                self.bouton.state(["disabled"])

                if self.tweet_reponse is None:
                    # On lance le tweet via ITwython
                    logger.debug("Tweet normal")
                    succes, msg = self.connexion.tweeter(message)
                else:
                    logger.debug("Tweet réponse à @" + self.tweet_reponse.user.screen_name)
                    succes, msg = self.connexion.tweeter("@" + self.tweet_reponse.user.screen_name + ' ' + message,
                                                         reponse=self.tweet_reponse.id)

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
        # self.texte_tweet.configure(state="normal")
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
        self.icone_aide = Label(self.cadre, anchor=tk.S, text=chr(int("E897", 16)), font=('Segoe MDL2 Assets', 20),
                                style="Sidebar.TLabel")
        self.icone_aide.bind("<Button-1>", lambda __: self.clic_aide())

        self.icone_utilisateur.grid(row=0, column=0, sticky="s")
        self.icone_option.grid(row=1, column=0, sticky="s", ipady=10)
        self.icone_aide.grid(row=2, column=0, sticky="s", ipady=10)

        self.cadre.grid_columnconfigure(0, weight=3)

    def clic_options(self):
        """Permet d'ouvrir la fenêtre de déconnection"""
        logger.debug("Clic options")
        fenetre_options = options_gui.FenetreOptions(self, self.parent.connexion.user)
        fenetre_options.grab_set()
        principal.wait_window(fenetre_options)

    def clic_utilisateur(self):
        """Permet de consulter le profil de l'utilisateur connecté"""
        logger.debug("Clic utilisateur")
        fenetre_utilisateur = user_gui.FenetreUtilisateur(self, self.parent.connexion.user)
        fenetre_utilisateur.grab_set()
        principal.wait_window(fenetre_utilisateur)

    def clic_aide(self):
        """Permet d'ouvrir la fenêtre d'aide."""
        logger.debug("Clic aide")
        fenetre_aide = options_gui.FenetreOptions(self, self.parent.connexion.user)
        fenetre_aide.grab_set()
        principal.wait_window(fenetre_aide)


class TweetGUI(Frame):
    """Cadre pour afficher un tweet unique, avec la photo de profil associée."""

    def __init__(self, parent, tweet: Tweet, timeline):
        logger.debug("Initialisation cadre : TweetGUI")
        Frame.__init__(self, parent)
        self.parent = parent
        self.timeline = timeline
        self.tweet = tweet
        self.id = tweet.id

        style = Style()
        style.configure("Test.TFrame", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TLabel", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("Name.TLabel", foreground="white", background="#343232", font=('Segoe UI', 14))
        style.configure("TFrame", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("Separateur.TFrame", foreground="white", background="white", font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 10))

        style.configure("Sidebar.TFrame", foreground="white", background="#111111", font=('Segoe UI', 10))
        style.configure("Sidebar.TLabel", foreground="white", background="#111111", font=('Segoe UI', 10))

        self.cadre_status = Frame(self, width=480, height=120)
        try:
            self.status = tk.Message(self.cadre_status, text=self.tweet.text,
                                     width=450, foreground="white", background="#343232",
                                     font=('Segoe UI', 10))
        except tk.TclError as e:
            logger.error(str(e))
            self.status = tk.Message(self.cadre_status, text=self.tweet.text.encode("utf-8"),
                                     width=450, foreground="white", background="#343232",
                                     font=('Segoe UI', 10))
        self.screen_name = Label(self, text="@" + self.tweet.user.screen_name, style="TLabel")
        try:
            self.name = Label(self, text=self.tweet.user.name, style="Name.TLabel")
        except tk.TclError as e:
            self.name = Label(self, text=self.tweet.user.name.encode("utf-8"), style="Name.TLabel")
        self.date = Label(self, text=self.tweet.date)

        separateur = Frame(self, width=580, height=2, style='Separateur.TFrame')
        separateur.grid(column=0, row=6, pady=4, columnspan=5)

        self.profile_picture = ProfilePictureGUI(self, self.tweet, cache_dir=self.timeline.cache_dir, tag=self.tweet.id)

        cadre_actions = Frame(self, width=580, height=50, style="TLabel")

        self.fav_variable = tk.StringVar()
        if not tweet.favorited:
            self.fav_variable.set(chr(int("E1CE", 16)))
        else:
            self.fav_variable.set(chr(int("E1CF", 16)))
        self.icone_fav = Label(cadre_actions, textvariable=self.fav_variable, font=('Segoe MDL2 Assets', 14),
                               style="TLabel")

        self.icone_rt = Label(cadre_actions, text=chr(int("E1CA", 16)), font=('Segoe MDL2 Assets', 14),
                              style="TLabel")

        self.icone_reply = Label(cadre_actions, text=chr(int("E15F", 16)), font=('Segoe MDL2 Assets', 14),
                                 style="TLabel")

        self.profile_picture.grid(column=0, row=0, pady=0, rowspan=1, sticky='NW')

        self.name.grid(column=1, row=0, pady=0, sticky='SW')
        self.screen_name.grid(column=2, row=0, sticky='S', pady=0)
        self.cadre_status.grid(column=1, row=1, columnspan=2, sticky='NW')
        # self.status.grid(column=1, row=1, columnspan=2, sticky='NW')
        self.status.grid(column=0, row=0)
        self.date.grid(column=0, columnspan=2, row=3, pady=0, sticky='W')

        cadre_actions.grid(column=2, row=3, columnspan=1, padx=0, pady=0, sticky='E')

        self.icone_reply.grid(column=0, row=0, pady=2, padx=00, sticky="")
        # self.likes_count.grid(column=1, row=5, pady=2)

        # self.fav_count.grid(column=2, row=5, pady=2)
        self.icone_fav.grid(column=1, row=0, pady=2, padx=00, sticky="E")
        # self.icone_fav_on.grid(column=2, row=5, pady=2)

        # self.rt_count.grid(column=3, row=5, pady=2)
        self.icone_rt.grid(column=2, row=0, pady=2, padx=00, sticky="E")

        Frame.grid_propagate(self)
        self.cadre_status.grid_propagate(0)

        # BINDING
        self.profile_picture.bindtags(self.tweet.id)
        self.name.bindtags(self.tweet.id)
        self.screen_name.bindtags(self.tweet.id)
        self.bind_class(self.tweet.id, "<Button-1>", lambda __: self.clic_utilisateur())
        self.icone_fav.bind("<Button-1>", lambda __: self.clic_fav())
        self.icone_rt.bind("<Button-1>", lambda __: self.clic_rt())
        self.icone_reply.bind("<Button-1>", lambda __: self.clic_reponse())

    def clic_fav(self):
        '''Permet de mettre un Tweet en favori'''
        logger.debug('Clic fav sur tweet (id) : ' + self.id)
        if not self.tweet.favorited:
            logger.debug('Tweet non fav')
            self.timeline.parent.connexion.fav(self.id)
            self.fav_variable.set(chr(int("E1CF", 16)))
            self.tweet.favorited = True
            # On ne change pas de Label, on change juste le texte
        else:
            logger.debug('Tweet fav')
            self.timeline.parent.connexion.defav(self.id)
            self.fav_variable.set(chr(int("E1CE", 16)))
            self.tweet.favorited = False

    def clic_rt(self):
        '''Permet d'appeler la fonction retweeter après un clic sur le bouton ReTweet'''
        logger.debug('Clic RT sur tweet (id) : ' + self.id)
        # TODO vérifier si le compte est protégé et si on peut RT ou pas
        self.timeline.parent.connexion.retweeter(self.id)

    def clic_reponse(self):
        '''Permet d'appeler la fonction mode_reponse après un clic sur le bouton Reply'''
        logger.debug('Clic reply sur tweet (id) : ' + self.id)
        self.timeline.parent.cadre_tweet.mode_reponse(self.tweet)

    def clic_utilisateur(self):
        '''Permet d'ouvrir le profil d'un utilisateur en cliquant sur son Username dans la Timeline'''
        logger.debug('Clic avatar sur tweet (id) : ' + self.id + ", utilisateur : " + self.tweet.user.id)
        fenetre_utilisateur = user_gui.FenetreUtilisateur(self, self.tweet.user)
        fenetre_utilisateur.grab_set()
        principal.wait_window(fenetre_utilisateur)


class ProfilePictureGUI(Frame):
    def __init__(self, parent, tweet: Tweet, cache_dir=path_finder.PathFinder.get_cache_directory(), tag=None):
        logger.debug("Initialisation cadre : photo de profil")

        Frame.__init__(self, parent)

        self.lien = tweet.user.profile_image_url_normal

        if self.lien is not None:
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
                # self.label.bindtags(tag)

            thread_tl = threading.Thread(target=action_async, daemon=True)
            thread_tl.start()


class TimeLine(Frame):
    def __init__(self, parent, stream_connection=True, static_connection=True):
        logger.debug("Initialisation cadre : timeline")
        style = Style()
        style.configure("Test.TFrame", foreground="white", background="#343232", font=('Segoe UI', 10))
        Frame.__init__(self, parent, style="Test.TFrame")
        self.parent = parent

        # On récupère le dossier de cache pour les photos
        self.cache_dir = path_finder.PathFinder.get_cache_directory()

        self.online = stream_connection

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1, minsize=500)

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
            tweets_data = self.parent.connexion.get_home_timeline(count=25)
            # Example de réponse dans dev_assets/list_tweets
            for tweet in reversed(tweets_data):
                self.add_data(tweet)

        if stream_connection:
            self.streamer = ITwython.ConnexionStream(self, parent.app_key, parent.app_secret,
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
            logger.debug(str(self.ligne) + " " + tweet.tweet.id)
            self.ligne = self.ligne + 1
            # self.scrollbar.grid_configure(rowspan=self.ligne + 1)

    def add_tweet(self, tweet: TweetGUI):
        tweet.grid(row=self.ligne, column=0)
        logger.debug(self.ligne + " " + tweet.id)
        self.ligne = self.ligne + 1

    def config_cadre(self, event):
        # D'après http://stackoverflow.com/questions/43766670/how-to-resize-a-scrollable-frame-to-fill-the-canvas
        # def onCanvasConfigure(self, event):

        # width is tweaked to account for window borders
        # TODO Bloquer scroll à la fin
        logger.debug("Reconfiguration Cadre TimeLine : " + str(event))
        logger.debug(self.scrollbar.get())
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        logger.debug(self.scrollbar.get())

        # height = event.height - 4
        # self.canvas.itemconfigure("self.frame", height=height)


# On commence le code ici
if __name__ == "__main__":
    logger.info("Démarrage de Twysn")

    # Principal est la racine de l'app
    principal = tk.Tk()
    principal.title("Twysn")
    principal.config(bg='#343232')
    principal.minsize(width=850, height=400)
    principal.call('tk', 'scaling', 2.0)

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
    app = App(principal, frozen=frozen)

    # On vérifie que l'application n'a pas été supprimée avec une erreur
    if app.existe:
        app.grid(sticky="nsew")
        app.columnconfigure(1, weight=1)
        app.rowconfigure(0, weight=1)

    principal.mainloop()
    app.quit()
    principal.quit()
    logger.info("Fermeture de Twysn")
    sys.exit()
