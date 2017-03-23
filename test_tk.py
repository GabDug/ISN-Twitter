from tkinter import *
from tkinter.ttk import *
import test_tweet


# Structure d'après
# https://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application
class App(Frame):
    def __init__(self, parent, connec, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.connec = connec

        tw = StringVar()

        texte = Label(self, text="Rédigez votre tweet : ")
        tweet = Entry(self, textvariable=tw)
        bouton = Button(self, text="Envoyer", command=lambda: test_tweet.Connec.tweeter(tw.get()))
        texte.pack()
        tweet.pack()
        bouton.pack()


if __name__ == "__main__":
    root = Tk()
    root.title("TwISN")
    root.config(bg='white')
    connec_ = test_tweet.Connec()
    App(root, connec_).pack(side="top", fill="both", expand=True)
    root.mainloop()

