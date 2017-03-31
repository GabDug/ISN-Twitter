from twython import *

from secrets import TWITTER_APP_KEY, TWITTER_APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

APP_KEY = TWITTER_APP_KEY
APP_SECRET = TWITTER_APP_SECRET
TOKEN = OAUTH_TOKEN
TOKEN_SECRET = OAUTH_TOKEN_SECRET


class Connec:
    def __init__(self):
        self.twython = Twython(APP_KEY, APP_SECRET, TOKEN, TOKEN_SECRET)
        print("###CONNEXION###")
        print(self.twython)
        print(self.twython.verify_credentials())
        print("###FIN###")
        # Connec.debugrate(Connec.twitter)

    def tweeter(self, txt):
        print("Tweet...")
        try:
            cred = self.twython.update_status(status=txt)
        except TwythonError as e:
            print("Erreur: " + str(e))
        print(cred)
        #Connec.debugrate(Connec.twitter)
        # print("x-rate-limit-limit:" + Connec.twitter.get_lastfunction_header('x-rate-limit-limit'))
        # print("x-rate-limit-remaining: " + Connec.twitter.get_lastfunction_header('x-rate-limit-remaining'))
        # print("x-rate-limit-reset: " + str(datetime.datetime.fromtimestamp(int(
        #     Connec.twitter.get_lastfunction_header('x-rate-limit-reset')))))
        # print("H: " + str(datetime.datetime.now()))

    @staticmethod
    def debugrate(twi):
        """Affiche les infos sur les limites d'utilisation"""
        print("DebugRate...")
        print(Connec.twitter)
        print(twi)
        # print("x-rate-limit-limit:" + twi.get_lastfunction_header('x-rate-limit-limit'))
        # print("x-rate-limit-remaining: " + twi.get_lastfunction_header('x-rate-limit-remaining'))
        # print("x-rate-limit-reset: " + str(datetime.datetime.fromtimestamp(int(
        #     twi.get_lastfunction_header('x-rate-limit-reset')))))
        # print("H: " + str(datetime.datetime.now()))
