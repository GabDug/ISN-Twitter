import tkinter as tk
from tkinter.ttk import *

import logger_conf
import path_finder

logger = logger_conf.Log.logger


class FenetreAide(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.config(bg='#343232')
        self.minsize(width=200, height=100)
        self.overrideredirect(False)

        self.title("Twysn")

        frozen, chemin_absolu = path_finder.PathFinder.get_icon_path()
        icon = tk.PhotoImage(file=chemin_absolu)
        self.tk.call('wm', 'iconphoto', self._w, icon)

        style = Style()
        style.configure("TLabel", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TFrame", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TEntry", foreground="black", background="#343232", font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 10))

        fenetre = Frame(self)
        fenetre.pack()

        cadre = Frame(fenetre)
        cadre.grid(row=0, column=0, padx=40, pady=20)

        titre = Label(cadre, text="Twysn", font=('Segoe UI Semilight', 24))
        version = Label(cadre, text="Version : 1.1")

        titre.grid(row=0, column=0)
        version.grid(column=0, row=1)
        # TODO Ajouter un texte avec, email, lien github, licenses, mails, description sommaire


# Permet d'éxécuter le code uniquement si lancé
# Pour tester
if __name__ == "__main__":
    root = tk.Tk()
    r = FenetreAide(root)
    r.grab_set()
    # root.call('tk', 'scaling', 2.0)
    root.mainloop()
