from tkinter import *
from tkinter.ttk import *


# TODO Créer une fenêtre enfant à partir de main_app.
def fenetreconnexion():
    root = Tk()
    root.title("Connexion")

    style = Style()
    style.configure("BW.TLabel", foreground="white", background="#343232")
    style.configure("A.BW.TLabel", foreground="white", background="#565656")

    fenetre = Frame(root, style="BW.TLabel")
    fenetre.pack()

    cadre = Frame(fenetre, style="BW.TLabel")
    cadre.grid(row=0, column=0, padx=50, pady=50)

    user = StringVar()
    password = StringVar()

    logophoto = PhotoImage(file="Twitter_Logo_Blue_Cropped.png")
    logo = Label(cadre, width=11, image=logophoto, style="BW.TLabel")
    logo.image = logophoto

    cadretexte = Frame(cadre, relief=GROOVE, style="A.BW.TLabel")
    cadretexte.grid(row=1, column=0, columnspan=2)

    titrelabel = Label(cadretexte, text="Bienvenue", style="A.BW.TLabel")
    userlabel = Label(cadretexte, text="Nom d'utilisateur : ", style="A.BW.TLabel")
    userentry = Entry(cadretexte, textvariable="user", style="A.BW.TLabel")
    passlabel = Label(cadretexte, text="Mot de passe : ", style="A.BW.TLabel")
    passentry = Entry(cadretexte, textvariable="password", show="*", style="A.BW.TLabel")

    # TODO Bouton connexion

    logo.grid(row=0, column=0, columnspan=2)
    titrelabel.grid(row=1, column=0, columnspan=2, pady=15)
    userlabel.grid(row=2, column=0, sticky="ew", padx=15)
    userentry.grid(row=2, column=1, sticky="ew", padx=15)
    passlabel.grid(row=3, column=0, sticky="ew", padx=15)
    passentry.grid(row=3, column=1, sticky="ew", padx=15, pady=5)

    userentry.focus()

    root.mainloop()


# Permet d'éxécuter le code uniquement si lancé
# Pas chargé
if __name__ == "__main__":
    fenetreconnexion()
