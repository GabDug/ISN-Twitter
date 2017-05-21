import tkinter as tk
import webbrowser
from tkinter.ttk import *

import logger_conf
import path_finder

logger = logger_conf.Log.logger


# TODO Faire menu clic droit pour copier/coller


class FenetreConnexion(tk.Toplevel):
    """Classe qui présente une fenêtre qui permet à l'utilisateur de se connecter."""

    def __init__(self, parent, co_temporaire, auth_url, test=False):
        tk.Toplevel.__init__(self, parent)
        self.overrideredirect(False)

        self.title("Twysn")

        # On récupère le chemin de l'icone et l'état de l'application( frozen = en .exe)
        frozen, chemin_absolu = path_finder.PathFinder.get_icon_path()
        icon = tk.PhotoImage(file=chemin_absolu)
        self.tk.call('wm', 'iconphoto', self._w, icon)

        self.connec_temporaire = co_temporaire

        self.pin_variable = tk.StringVar()
        self.pin_link = auth_url

        # Définit un état de cadre_status pour la mise en page : si True, alors les actions ne sont pas réalisées
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

        titreconnexion = Label(cadre, text="Connexion", font=('Segoe UI Semilight', 24))

        message_info_1 = Label(cadre,
                               text="Vous devez vous connecter sur twitter.com dans la page qui vient de s'ouvrir. ")
        message_info_2 = Label(cadre, text="Vous obtiendrez ainsi un code à usage unique pour vous connecter à TwISN.")
        message_info_3 = Label(cadre, text="Cliquez ici pour réouvrir la page.")

        # On imbrique les frames pour une mise en page plus simple
        frame_code = Frame(cadre)
        codelabel = Label(frame_code, text="Code de connexion")
        codeentry = Entry(frame_code, textvariable=self.pin_variable)
        bouton = Button(cadre, command=self.connexion, text="Connexion")

        titreconnexion.grid(column=0, row=0, sticky="w", pady=10)
        message_info_1.grid(row=1, column=0, columnspan=2, sticky="w")
        message_info_2.grid(row=2, column=0, columnspan=2, sticky="w")
        message_info_3.grid(row=3, column=0, columnspan=2, sticky="w")
        frame_code.grid(row=4, column=0, columnspan=2, sticky="w", pady=20)
        codelabel.grid(row=0, column=0, sticky="w")
        codeentry.grid(row=1, column=0, sticky="w")
        bouton.grid(row=6, column=0, sticky="e", columnspan=2)

        message_info_3.bind("<Button-1>", lambda __: self.ouverture_lien())

        # Focus de l'entrée clavier sur le code
        codeentry.focus()

        # TODO appuyer sur le bouton si enter

        # On ouvre automatiquement le lien
        self.ouverture_lien()

    def ouverture_lien(self):
        if not self.test:
            webbrowser.open_new(self.pin_link)

    def connexion(self):
        # from main_app import final
        import main_app
        logger.debug("Code entré : " + str(self.pin_variable.get()))

        # Si on n'est pas en train de faire la mise en page (pas debug)
        if not self.test:
            # On renvoie le code pin reçu à main_app
            main_app.App.final(self, self.connec_temporaire, self.pin_variable.get())
        # On ferme la fenêtre de connexion
        self.destroy()


# Permet d'éxécuter le code uniquement si lancé directement
# Pour tester et faire la mise en page
if __name__ == "__main__":
    root = tk.Tk()
    r = FenetreConnexion(root, "", "<lien>", test=True)
    r.grab_set()
    # root.call('tk', 'scaling', 2.0)
    root.mainloop()
