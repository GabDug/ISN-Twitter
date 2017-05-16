import os
import threading
import tkinter as tk
import urllib
from tkinter.ttk import *

from PIL import Image, ImageTk

import logger_conf
import path_finder
from ITwython import User

logger = logger_conf.Log.logger


# TODO Faire menu clic droit pour copier/coller


class ProfilePictureGUI(Frame):
    def __init__(self, parent, user):
        logger.debug("Initialisation cadre : photo de profil")
        Frame.__init__(self, parent)

        self.lien = user.profile_image_url

        # TODO Fixer le lien si l'app est frozen
        # On supprime les : et / de l'url pour en faire un nom de fichier
        save_relatif = self.lien.replace("http://", "").replace("https://", "").replace(":", "").replace("/", ".")
        # On obtient le répertoire de sauvegarde des photos
        cache_dir = path_finder.PathFinder.get_cache_directory()
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
                    logger.error("HTTP ERROR PROFILE PICTURE !" + str(e))
                    return

            # TODO Ajouter exception pour ouverture fichier
            self.pil_image = Image.open(self.save)
            self.pil_image.thumbnail((100, 100))
            self.photo = ImageTk.PhotoImage(self.pil_image)

            label = Label(self, image=self.photo)
            label.pack(padx=5, pady=5)

        thread_tl = threading.Thread(target=action_async, daemon=True)
        thread_tl.start()


class FenetreUtilisateur(tk.Toplevel):
    def __init__(self, parent, utilisateur, test=False):
        tk.Toplevel.__init__(self, parent)
        self.overrideredirect(False)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # TODO Choisir entre TwISN ou Twyisn
        self.title("TwISN")

        frozen, chemin_absolu = path_finder.PathFinder.get_icon_path()
        icon = tk.PhotoImage(file=chemin_absolu)
        self.tk.call('wm', 'iconphoto', self._w, icon)

        self.utilisateur = utilisateur

        self.pin_variable = tk.StringVar()

        self.test = test

        style = Style()
        style.configure("TLabel", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TFrame", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TEntry", foreground="black", background="#343232", font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 10))

        fenetre = Frame(self)
        fenetre.grid(row=0, column=0, sticky="nsew")
        fenetre.columnconfigure(0, weight=1)
        fenetre.rowconfigure(0, weight=1)

        cadre = Frame(fenetre)
        cadre.grid(row=0, sticky="nsew", column=0, padx=10, pady=10)
        cadre.columnconfigure(0, weight=1)
        cadre.rowconfigure(0, weight=1)


        cadre_titre = Frame(cadre)
        cadre_titre.grid(row=0, column=1)

        name = self.utilisateur.name
        screen_name = self.utilisateur.screen_name

        try:
            nom_long = Label(cadre_titre, text=name, font=('Segoe UI Semilight', 24))
        except tk.TclError as e:
            logger.error(e)
            nom_long = Label(cadre_titre, text=name.encode("utf-8"), font=('Segoe UI Semilight', 24))

        try:
            nom_at = Label(cadre_titre, text="@" + screen_name, font=('Segoe UI Semilight', 18))
        except tk.TclError as e:
            logger.error(e)
            nom_at = Label(cadre_titre, text=screen_name.encode("utf-8"), font=('Segoe UI Semilight', 18))
        # nom_long = Label(cadre_titre, text="Gabriel Dugny",
        #                  font=('Segoe UI Semilight', 24))
        # nom_at = Label(cadre_titre, text="@DUGNYCHON",
        #                font=('Segoe UI Semilight', 18))
        nom_long.grid(column=0, row=0, sticky="ws", pady=10)
        nom_at.grid(column=1, row=0, sticky="ws", pady=10)

        cadre_description = Frame(cadre)
        cadre_description.grid(row=1, column=1, pady=10)

        description = self.utilisateur.description
        location = self.utilisateur.location
        try:
            description = Label(cadre_description, text=description)
        except tk.TclError as e:
            logger.error(e)
            description = Label(cadre_description, text=description.encode("utf-8"))

        try:
            location = Label(cadre_description, text="@" + location)
        except tk.TclError as e:
            logger.error(e)
            location = Label(cadre_description, text=location.encode("utf-8"))

        description.grid(row=0, column=0, sticky="w")
        location.grid(row=1, column=0, sticky="w")

        cadre_compteurs = Frame(cadre)
        cadre_compteurs.grid(row=2, column=0, columnspan=2, sticky="ws")
        cadre_compteurs.columnconfigure(0, weight=1)
        cadre_compteurs.rowconfigure(0, weight=1)

        message_tweets = Label(cadre_compteurs, text="Tweets")
        compteur_tweets = Label(cadre_compteurs, text=self.utilisateur.statuses_count)

        message_abonnements = Label(cadre_compteurs, text="Abonnements")
        compteur_abonnements = Label(cadre_compteurs, text=self.utilisateur.friends_count)

        message_abonnes = Label(cadre_compteurs, text="Abonnés")
        compteur_abonnes = Label(cadre_compteurs, text=self.utilisateur.followers_count)

        self.profile_picture = ProfilePictureGUI(cadre, self.utilisateur)
        self.profile_picture.grid(row=0, column=0, rowspan=1, sticky="w")

        nom_long.grid(column=0, row=0, sticky="w", pady=10)
        nom_at.grid(column=1, row=0, sticky="w", pady=10)

        # logo.grid(row=1, column=0, columnspan=2)
        message_tweets.grid(row=0, column=0, sticky="w")
        compteur_tweets.grid(row=1, column=0, sticky="w")
        message_abonnements.grid(row=0, column=1, padx=10, sticky="we")
        compteur_abonnements.grid(row=1, column=1, padx=10, sticky="we")
        message_abonnes.grid(row=0, column=2, sticky="e")
        compteur_abonnes.grid(row=1, column=2, sticky="e")


# Permet d'éxécuter le code uniquement si lancé
# Pour tester
if __name__ == "__main__":
    from dev_assets import user_example

    root = tk.Tk()
    r = FenetreUtilisateur(root, User(user_example.c), test=True)
    r.grab_set()
    # root.call('tk', 'scaling', 2.0)
    root.mainloop()
