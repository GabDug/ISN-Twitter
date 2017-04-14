import os.path
import tkinter as tk
import webbrowser
from tkinter.ttk import *
import logging

chemin_relatif = "/../assets/Twitter_Logo_Blue_Cropped.png"
chemin_absolu = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + chemin_relatif)


class FenetreConnexion:
    def __init__(self, co_temporaire, auth_url, test=False):
        self.root = tk.Toplevel()
        self.root.title("Twysn - Connexion")

        self.connec_temporaire = co_temporaire

        self.pin_variable = tk.StringVar()
        self.pin_link = auth_url

        self.test = test

        style = Style()
        style.configure("BW.TLabel", foreground="white", background="#343232")
        style.configure("A.BW.TLabel", foreground="white", background="#565656")

        fenetre = Frame(self.root, style="BW.TLabel")
        fenetre.pack()

        cadre = Frame(fenetre, style="BW.TLabel")
        cadre.grid(row=0, column=0, padx=50, pady=50)

        logophoto = tk.PhotoImage(file=chemin_absolu)
        logo = Label(cadre, width=11, image=logophoto, style="BW.TLabel")
        logo.image = logophoto

        cadretexte = Frame(cadre, relief=tk.GROOVE, style="A.BW.TLabel")
        cadretexte.grid(row=1, column=0, columnspan=2)

        titrelabel = Label(cadretexte, text="Le code est présent sur la page qui vient de s'ouvrir.",
                           style="A.BW.TLabel")
        codelabel = Label(cadretexte, text="Code connexion : ", style="A.BW.TLabel")
        codeentry = Entry(cadretexte, textvariable=self.pin_variable, style="A.BW.TLabel")
        bouton = Button(cadretexte, command=self.connexion, text="Connexion")

        logo.grid(row=0, column=0, columnspan=2)
        titrelabel.grid(row=1, column=0, columnspan=2, pady=15)
        codelabel.grid(row=3, column=0, sticky="ew", padx=15)
        codeentry.grid(row=3, column=1, sticky="ew", padx=15, pady=5)
        bouton.grid(row=4, column=0, columnspan=2, sticky="ew")

        codeentry.focus()
        self.ouverture_lien()

    def ouverture_lien(self):
        webbrowser.open_new(self.pin_link)

    def connexion(self):
        from main_app import final
        logging.debug("Input Pin = " + str(self.pin_variable.get()))
        if not self.test:
            final(self.root, self.connec_temporaire, self.pin_variable.get())
        self.root.destroy()


# Permet d'éxécuter le code uniquement si lancé
# Pour tester
if __name__ == "__main__":
    r = tk.Tk()
    r = FenetreConnexion("", "<lien>", test=True)
    r.root.mainloop()
