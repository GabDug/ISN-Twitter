from twython import *

from src import token_manager

# On récupère les différents tokens
# On est normalement assuré des 4 éléments donc on peux utiliser l'unpacking
# http://python-guide-pt-br.readthedocs.io/en/latest/writing/style/#unpacking
APP_KEY, APP_SECRET, TOKEN, TOKEN_SECRET = token_manager.get_tokens()


class Connec:
    def __init__(self):
        print("DD")
        self.twython = Twython(APP_KEY, APP_SECRET, TOKEN, TOKEN_SECRET)
        # except AttributeError as e:
        #     print("Erreur ! Connexion impossible!")
        #     print(e)
        #     self.twython = None
        print("###CONNEXION###")
        print(self.twython)
        print(self.twython.verify_credentials())
        print("###FIN###")
        # Connec.debugrate(Connec.twitter)

    def tweeter(self, txt):
        print("Tweet...")
        try:
            cred = self.twython.update_status(status=txt)
            print("B")
        except TwythonError as e:
            print("Erreur: " + str(e))
        print(cred)
        # Connec.debugrate(Connec.twitter)
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
