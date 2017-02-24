import datetime

from twython import *

from secrets import TWITTER_APP_KEY, TWITTER_APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

APP_KEY = TWITTER_APP_KEY
APP_SECRET = TWITTER_APP_SECRET
TOKEN = OAUTH_TOKEN
TOKEN_SECRET = OAUTH_TOKEN_SECRET


class Connec:
    twitter = Twython()

    def __init__(self):
        Connec.twitter = Twython(APP_KEY, APP_SECRET, TOKEN, TOKEN_SECRET)
        print(Connec.twitter)
        print(Connec.twitter.verify_credentials())
        Connec.debugrate()

    @staticmethod
    def tweeter(txt):
        print("Tweet...")
        try:
            cred = Connec.twitter.update_status(status=txt)
        except TwythonError as e:
            print("Erreur: "+str(e))
        print(cred)
        Connec.debugrate()

    @staticmethod
    def debugrate():
        "Affiche les infos sur les limites d'utilisation"

        print("x-rate-limit-limit:" + Connec.twitter.get_lastfunction_header('x-rate-limit-limit'))
        print("x-rate-limit-remaining: " + Connec.twitter.get_lastfunction_header('x-rate-limit-remaining'))
        print("x-rate-limit-reset: " + str(datetime.datetime.fromtimestamp(int(
            Connec.twitter.get_lastfunction_header('x-rate-limit-reset')))))
        print("H: " + str(datetime.datetime.now()))
