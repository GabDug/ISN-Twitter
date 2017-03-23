from tkinter import *
from tkinter.ttk import *

root = Tk()
root.title("Connexion")

cadre = Frame(root)
cadre.grid(row=0, column=0)

user = StringVar()
password = StringVar()

logophoto = PhotoImage(file="Twitter_Logo_Blue.png")
logo = Label(cadre, image=logophoto)
logo.image = logophoto
userlabel = Label(cadre, text="Nom d'utilisateur : ")
userentry = Entry(cadre, textvariable="user")
passlabel = Label(cadre, text="Mot de passe : ")
passentry = Entry(cadre, textvariable="password", show="*")

logo.grid(row=0, column=0, columnspan=1)
userlabel.grid(row=1, column=0,sticky="ew", padx=15)
userentry.grid(row=1, column=1,sticky="ew", padx=15)
passlabel.grid(row=2, column=0, sticky="ew", padx=15)
passentry.grid(row=2, column=1, sticky="ew", padx=15, pady=15)

root.mainloop()
