import os
import threading
import tkinter as tk
import urllib
import webbrowser
from tkinter.ttk import *

from PIL import Image, ImageTk

from ITwython import Tweet, User
import logger_conf
import path_finder

logger = logger_conf.Log.logger


# TODO Faire menu clic droit pour copier/coller


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
        # logger.debug("Dossier cache : " + cache_dir)

        # On crée un string avec le lien absolu vers le fichier
        self.save = cache_dir + "/" + save_relatif
        logger.debug("Fichier cache : " + self.save)


        def action_async():
            # Si le fichier n'existe pas alors on le télécharge
            if not os.path.isfile(self.save):
                logger.debug("Téléchargement du fichier : "+self.save)
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

        thread_tl = threading.Thread(target=action_async, daemon=True)
        thread_tl.start()



class FenetreUtilisateur(tk.Toplevel):
    def __init__(self, parent, utilisateur, test=False):
        tk.Toplevel.__init__(self, parent)
        self.overrideredirect(False)

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
        fenetre.pack()

        cadre = Frame(fenetre)
        cadre.grid(row=0, column=0, padx=40, pady=20)

        cadre_titre = Frame(cadre)
        cadre_titre.grid(row=0, column=0)

        nom_long = Label(cadre_titre, text="Gabriel Dugny",
                         font=('Segoe UI Semilight', 24))
        nom_at = Label(cadre_titre, text="@DUGNYCHON",
                       font=('Segoe UI Semilight', 18))
        nom_long.grid(column=0, row=0, sticky="w", pady=10)
        nom_at.grid(column=1, row=0, sticky="ws", pady=10)

        cadre_description = Frame(cadre)
        cadre_description.grid(row=1, column=0, pady=10)

        description = Label(cadre_description, text="Mec super cool.\nPas responsable du cool.")
        localisation = Label(cadre_description, text="Paris, France")

        description.grid(row=0, column=0, sticky="w")
        localisation.grid(row=1, column=0, sticky="w")


        cadre_compteurs = Frame(cadre)
        cadre_compteurs.grid(row=2, column=0,sticky="ws")

        message_tweets = Label(cadre_compteurs, text="Tweets")
        compteur_tweets = Label(cadre_compteurs, text="10 568")

        message_abonnements = Label(cadre_compteurs, text="Abonnements")
        compteur_abonnements = Label(cadre_compteurs, text="208")

        message_abonnes = Label(cadre_compteurs, text="Abonnés")
        compteur_abonnes = Label(cadre_compteurs, text="569")
        #
        # message_info_2 = Label(cadre, text="Vous obtiendrez ainsi un code à usage unique pour vous connecter à TwISN.")
        # frame_code = Frame(cadre)
        #
        # bouton = Button(cadre, command=self.connexion, text="Connexion")

        nom_long.grid(column=0, row=0, sticky="w", pady=10)
        nom_at.grid(column=1, row=0, sticky="w", pady=10)

        # logo.grid(row=1, column=0, columnspan=2)
        message_tweets.grid(row=0, column=0, sticky="w")
        compteur_tweets.grid(row=1, column=0, sticky="w")
        message_abonnements.grid(row=0, column=1, sticky="w")
        compteur_abonnements.grid(row=1, column=1, sticky="w")
        message_abonnes.grid(row=0, column=2, sticky="w")
        compteur_abonnes.grid(row=1, column=2, sticky="w")

        # frame_code.grid(row=3, column=0, columnspan=2, sticky="w", pady=20)
        # bouton.grid(row=5, column=0, sticky="e", columnspan=2)

    def ouverture_lien(self):
        if not self.test:
            webbrowser.open_new(self.pin_link)

    def connexion(self):
        from main_app import final
        logger.debug("Code entré : " + str(self.pin_variable.get()))

        # Si on n'est pas en train de faire la mise en page (pas debug)
        if not self.test:
            final(self, self.connec_temporaire, self.pin_variable.get())
        self.destroy()


# Permet d'éxécuter le code uniquement si lancé
# Pour tester
if __name__ == "__main__":
    root = tk.Tk()
    r = FenetreUtilisateur(root, None, test=True)
    r.grab_set()
    # root.call('tk', 'scaling', 2.0)
    root.mainloop()
