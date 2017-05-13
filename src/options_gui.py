import tkinter as tk
from tkinter.ttk import *

from dev_assets import user_example

import logger_conf
import path_finder
from ITwython import User
from token_manager import delete_tokens

logger = logger_conf.Log.logger


# TODO Faire menu clic droit pour copier/coller


class FenetreOptions(tk.Toplevel):
    def __init__(self, parent, utilisateur, test=False):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent

        self.overrideredirect(False)

        # TODO Choisir entre TwISN ou Twyisn
        self.title("TwISN")

        frozen, chemin_absolu = path_finder.PathFinder.get_icon_path()
        icon = tk.PhotoImage(file=chemin_absolu)
        self.tk.call('wm', 'iconphoto', self._w, icon)

        self.test = test

        self.utilisateur = utilisateur
        nom_at = "@" + self.utilisateur.screen_name

        style = Style()
        style.configure("TLabel", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TFrame", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TEntry", foreground="black", background="#343232", font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 10))

        fenetre = Frame(self)
        fenetre.pack()

        cadre = Frame(fenetre)
        cadre.grid(row=0, column=0, padx=40, pady=20)

        titreoptions = Label(cadre, text="Options", font=('Segoe UI Semilight', 24))

        message_cache = Label(cadre, text="Supprimer les données en cache.")
        separateur_cache = Label(cadre, text="")
        bouton_cache = Button(cadre, text="Supprimer")

        message_deconnexion = Label(cadre, text="Connecté au compte {0}".format(nom_at))
        bouton_deconnexion = Button(cadre, command=self.deconnexionquitter, text="Se déconnecter et quitter")

        titreoptions.grid(column=0, row=0, sticky="w", pady=10)

        message_cache.grid(row=1, column=0, columnspan=2, sticky="w")
        separateur_cache.grid(row=1, column=2, padx=20, sticky="w")
        bouton_cache.grid(row=1, column=3, pady=20, sticky="e")

        message_deconnexion.grid(row=6, column=0, sticky="w", columnspan=2)
        bouton_deconnexion.grid(row=6, column=3, sticky="e", columnspan=2)

    def deconnexionquitter(self):
        try:
            delete_tokens()
            self.parent.parent.parent.quit()  # (Principal dans main_app)
            self.destroy()
        except:
            logger.error("Impossible de quitter.")
            pass

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
    r = FenetreOptions(root, User(user_example.c), test=True)
    r.grab_set()
    # root.call('tk', 'scaling', 2.0)
    root.mainloop()
