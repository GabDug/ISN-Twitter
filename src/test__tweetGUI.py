import os
import tkinter as tk
import urllib
from tkinter import *
from tkinter.ttk import *
from urllib.request import urlopen

from PIL import Image, ImageTk

import logger_conf
import path_finder

logger = logger_conf.Log.logger

'''
fenetre = Tk()

labelframe = LabelFrame(fenetre, text="This is a LabelFrame")
labelframe.pack(fill="both", expand="yes")
 
left = Label(labelframe, text="Inside the LabelFrame")
left.pack()

frame = Frame(fenetre)
frame.pack()

redbutton = Button(frame, text="Red", fg="red")
redbutton.pack( side = LEFT)

greenbutton = Button(frame, text="Green", fg="green")
greenbutton.pack( side = LEFT )

bluebutton = Button(frame, text="Blue", fg="blue")
bluebutton.pack( side = LEFT )

fenetre.mainloop()
'''


class TweetGUI(Frame):
    """Cadre pour afficher un tweet unique."""

    def __init__(self, parent):

        Frame.__init__(self, parent)

        style = Style()
        style.configure("Test.TFrame", foreground="white", background="blue", font=('Segoe UI', 10))
        style.configure("TLabel", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TFrame", foreground="white", background="#343232", font=('Segoe UI', 10))
        style.configure("TEntry", foreground="red", background="#343232", font=('Segoe UI', 10))
        style.configure("TButton", font=('Segoe UI', 10))

        style.configure("Sidebar.TFrame", foreground="white", background="#111111", font=('Segoe UI', 10))
        style.configure("Sidebar.TLabel", foreground="white", background="#111111", font=('Segoe UI', 10))

        self.parent = parent
        # self.connec = parent.connec

        # On met en place le cadre du tweet

        screen_name = "DUGNYCHON"  # self.tweet.user.screen_name.encode("utf-8").decode('utf-8')
        name = 'Gabi'  # self.tweet.user.name.encode("utf-8").decode('utf-8')
        status = 'Quentin il est vraiment trop fort il me rend fier felicitez le pour moi ptn'  # self.tweet.text.encode("utf-8").decode('utf-8')
        date = '04/05/2017 10:20'  # 'self.tweet.created_at.encode("utf-8").decode('utf-8')

        # self.profile_image = Label(self, image=None)
        try:
            self.status = tk.Message(self, text=status, width=100, foreground="white", background="#343232",
                                     font=('Segoe UI', 10))
        except tk.TclError as e:
            self.status = tk.Message(self, text=status.encode("utf-8"), width=380, foreground="white",
                                     background="#343232", font=('Segoe UI', 10))

        try:
            self.name = Label(self, text=name)
        except tk.TclError as e:
            self.name = Label(self, text=name.encode("utf-8"))

        try:
            self.screen_name = Label(self, text="@" + screen_name)
        except tk.TclError as e:
            pass

        self.date = Label(self, text=date)

        self.lien = "https://pbs.twimg.com/profile_images/817042499134980096/LTpqSDMM_bigger.jpg"
        save_relatif = self.lien.replace(":", "").replace("/", "")
        cache_dir = ""
        # On crée un string avec le lien absolu vers le fichier
        self.save = save_relatif

        if os.path.isfile(self.save):
            print("File already exists ! ")
        # Sinon on le télécharge
        else:

            try:
                testfile = urllib.request.URLopener()
                testfile.retrieve(self.lien, self.save)
                # aa = "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"
                # internal data file
                # data_stream = io.BytesIO(aa)
                # open as a PIL image object

            except urllib.error.HTTPError as e:
                print("HTTP ERROR PROFILE PICTURE !" + str(e))
                return

        cadre1 = Frame(self, cursor='dot', width=500, height=500, style="TEntry")
        cadre1.grid(column=0, row=0, rowspan=5, columnspan=5, padx=5, pady=5)

        cadre2 = Frame(self, cursor='arrow', width=100, height=100, style="Test.TFrame")
        cadre2.grid(column=0, row=0, rowspan=2, padx=20, pady=20, sticky='N')

        separateur = Frame(self, width=500, height=8)
        separateur.grid(column=0, row=6, columnspan=5)

        # self.profile_picture = ProfilePictureGUI(self)
        self.image = Image.open(self.save)
        self.profile_picture = ImageTk.PhotoImage(self.image)
        label = Label(self, image=self.profile_picture)

        self.likes_count = Label(self, text="Likes: 12")
        self.fav_count = Label(self, text="Favoris: 0")
        self.rt_count = Label(self, text="Retweet: 1")
        self.name = Label(self, text='Gabigabigoooo a dit:')
        self.screen_name = Label(self, text='@DUGNYCHON_DIVIN')

        label.grid(column=0, row=0, pady=30, rowspan=2, sticky='N')
        self.name.grid(column=1, row=0, pady=30, sticky='N')
        self.screen_name.grid(column=1, row=0, pady=5)
        self.status.grid(column=2, row=1, sticky='N')
        self.date.grid(column=3, row=3, sticky='')

        self.likes_count.grid(column=1, row=5, pady=2)
        self.fav_count.grid(column=2, row=5, pady=2)
        self.rt_count.grid(column=3, row=5, pady=2)


class ProfilePictureGUI(Frame):
    def __init__(self, parent):
        logger.debug("Initialisation cadre : photo de profil")
        Frame.__init__(self, parent)

        # self.lien = tweet.user.profile_image_url
        self.lien = 'https://pbs.twimg.com/profile_images/1673907275/image.jpg'

        # TODO Fixer le lien si l'app est frozen
        # On supprime les : et / de l'url pour en faire un nom de fichier
        save_relatif = self.lien.replace("http://", "").replace("https://", "").replace(":", "").replace("/", ".")
        # On obtient le répertoire de sauvegarde des photos
        cache_dir = path_finder.PathFinder.get_cache_directory()
        logger.debug("Dossier cache : " + cache_dir)

        # On crée un string avec le lien absolu vers le fichier
        self.save = save_relatif
        logger.debug("Fichier cache : " + self.save)

        # Si le fichier n'existe pas alors on le télécharge
        if not os.path.isfile(self.save):
            logger.debug("Téléchargement du fichier.")
            try:
                testfile = urllib.request.URLopener()
                testfile.retrieve(self.lien, self.save)
                # aa = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gKgSUNDX1BST0ZJTEUAAQEAAAKQbGNtcwQwAABtbnRyUkdCIFhZWiAH4QAEAA0AEgAnAAdhY3NwQVBQTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9tYAAQAAAADTLWxjbXMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtkZXNjAAABCAAAADhjcHJ0AAABQAAAAE53dHB0AAABkAAAABRjaGFkAAABpAAAACxyWFlaAAAB0AAAABRiWFlaAAAB5AAAABRnWFlaAAAB+AAAABRyVFJDAAACDAAAACBnVFJDAAACLAAAACBiVFJDAAACTAAAACBjaHJtAAACbAAAACRtbHVjAAAAAAAAAAEAAAAMZW5VUwAAABwAAAAcAHMAUgBHAEIAIABiAHUAaQBsAHQALQBpAG4AAG1sdWMAAAAAAAAAAQAAAAxlblVTAAAAMgAAABwATgBvACAAYwBvAHAAeQByAGkAZwBoAHQALAAgAHUAcwBlACAAZgByAGUAZQBsAHkAAAAAWFlaIAAAAAAAAPbWAAEAAAAA0y1zZjMyAAAAAAABDEoAAAXj///zKgAAB5sAAP2H///7ov///aMAAAPYAADAlFhZWiAAAAAAAABvlAAAOO4AAAOQWFlaIAAAAAAAACSdAAAPgwAAtr5YWVogAAAAAAAAYqUAALeQAAAY3nBhcmEAAAAAAAMAAAACZmYAAPKnAAANWQAAE9AAAApbcGFyYQAAAAAAAwAAAAJmZgAA8qcAAA1ZAAAT0AAACltwYXJhAAAAAAADAAAAAmZmAADypwAADVkAABPQAAAKW2Nocm0AAAAAAAMAAAAAo9cAAFR7AABMzQAAmZoAACZmAAAPXP/bAEMABQMEBAQDBQQEBAUFBQYHDAgHBwcHDwsLCQwRDxISEQ8RERMWHBcTFBoVEREYIRgaHR0fHx8TFyIkIh4kHB4fHv/bAEMBBQUFBwYHDggIDh4UERQeHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHv/CABEIADAAMAMBIgACEQEDEQH/xAAaAAACAgMAAAAAAAAAAAAAAAACBgUHAAME/8QAGgEAAgIDAAAAAAAAAAAAAAAAAwQAAgEFBv/aAAwDAQACEAMQAAABt2PxWqZi2oOsDFmkkNx1Y1AZkRPfiXDlgtjrVTCM8zXdm14TMAPaanUjOQLDEP/EAB8QAAIDAQADAAMAAAAAAAAAAAIDAAEEEQUSIRMjMf/aAAgBAQABBQIyhMlu5B2clMopRR7OTXqoJW2N8idX43dR3V/NRfNvTZxiIhl6bzIBI4nfkT5B9ALNEN5MgGAROm2H47dSm7BqbPjCq++t3K4oUL/Xrzlc3Bw/7PgVnD3Z7T//xAAhEQABBAEDBQAAAAAAAAAAAAACAAEDBBETFDEFITJBgf/aAAgBAwEBPwEAytv2RxuKqwxEDt7W2POMK7WEK4i/k/C6ZBqPhbYeXUdUjm1z+Mv/xAAcEQACAgMBAQAAAAAAAAAAAAAAAgERAxMhEjH/2gAIAQIBAT8BaaNs2K1mV2vhfO/TCzQ/TPNGwyPUeYP/xAAkEAACAQQBAgcAAAAAAAAAAAAAARICEBEhQgMiEyAxMkFRYf/aAAgBAQAGPwK2juRlPydrzb8+VfTG85I9VaHCoX2M16m3gz4jI8RUPmxjjePJk37maqHaRKowf//EACAQAQACAQQCAwAAAAAAAAAAAAEAESExQVFhEHGBkaH/2gAIAQEAAT8hAgF5hrK3qaF65hdZGYJQYa007Slqxuw1ehMVUWptCyIVpZGAal30BKKTpFb7YShwKYg5fUxKOUzfbqJwiroP2Z0MAcHMeWhDYF+EGVcQvZDiVPSiuoU2fMrbSjrKHKti3YiM151mFWn/2gAMAwEAAgADAAAAEHM8F+Jip7P/xAAcEQEAAwACAwAAAAAAAAAAAAABABEhMVFBkcH/2gAIAQMBAT8QWK8mM7w+ZfLZkKYVQCtMHqJQ57malBKWVWdQfWf/xAAaEQEAAwEBAQAAAAAAAAAAAAABABExQSFR/9oACAECAQE/ENUHoEAfGBJiN2wcq87BrLYbKrTs/8QAHxABAAICAgMBAQAAAAAAAAAAAQARITFBYVFxgZGx/9oACAEBAAE/ECXNRKwO7lK6TaOgfmMpNuTCMK3MC5LbVaHcd6F7FnBO0lQYuIcw8xVixOJcxMXzMMVB7gihlvijp4sUVUY84vLMuViDuJPCOIduQaEVAF4NRqlfIb+QIZWq59pXmCsad+kwVenmEwYAeJc2t9QrYwrtgOx0+/yCfG+PDwSk7jYEmeDNMWRxBk2QVF+sxK1rK5YkhhWCf//ZICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA="
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


if __name__ == '__main__':
    t = tk.Tk()
    tweet = TweetGUI(t)
    tweet.pack()
    t.mainloop()
