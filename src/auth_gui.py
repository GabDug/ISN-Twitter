import tkinter as tk
import webbrowser
from tkinter.ttk import *

import logger_conf
import path_finder

logger = logger_conf.Log.logger


# TODO Faire menu clic droit pour copier/coller


class FenetreConnexion(tk.Toplevel):
    def __init__(self, parent, co_temporaire, auth_url, test=False):
        tk.Toplevel.__init__(self, parent)
        self.overrideredirect(False)

        # TODO Choisir entre TwISN ou Twyisn
        self.title("TwISN")

        frozen, chemin_absolu = path_finder.PathFinder.get_icon_path()
        icon = tk.PhotoImage(file=chemin_absolu)
        self.tk.call('wm', 'iconphoto', self._w, icon)

        self.connec_temporaire = co_temporaire

        self.pin_variable = tk.StringVar()
        self.pin_link = auth_url

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

        titreconnexion = Label(cadre, text="Connexion",
                               font=('Segoe UI Semilight', 24))

        message_info_1 = Label(cadre,
                               text="Vous devez vous connecter sur twitter.com dans la page qui vient de s'ouvrir. ")
        message_info_2 = Label(cadre, text="Vous obtiendrez ainsi un code à usage unique pour vous connecter à TwISN.")
        frame_code = Frame(cadre)
        codelabel = Label(frame_code, text="Code de connexion")
        codeentry = Entry(frame_code, textvariable=self.pin_variable)
        bouton = Button(cadre, command=self.connexion, text="Connexion")

        titreconnexion.grid(column=0, row=0, sticky="w", pady=10)
        # logo.grid(row=1, column=0, columnspan=2)
        message_info_1.grid(row=1, column=0, columnspan=2, sticky="w")
        message_info_2.grid(row=2, column=0, columnspan=2, sticky="w")
        frame_code.grid(row=3, column=0, columnspan=2, sticky="w", pady=20)
        codelabel.grid(row=0, column=0, sticky="w")
        codeentry.grid(row=1, column=0, sticky="w")
        bouton.grid(row=5, column=0, sticky="e", columnspan=2)

        codeentry.focus()
        self.ouverture_lien()

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
    r = FenetreConnexion(root, "", "<lien>", test=True)
    r.grab_set()
    # root.call('tk', 'scaling', 2.0)
    root.mainloop()
