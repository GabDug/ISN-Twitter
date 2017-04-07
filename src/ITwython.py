from twython import *


class ConnecTemporaire:
    def __init__(self, _app_token, _app_secret):
        self.app_token = _app_token
        self.app_secret = _app_secret
        print(self.app_token)
        print(self.app_secret)

        self.connection = Twython(self.app_token, self.app_secret)
        auth = self.connection.get_authentication_tokens()
        # On obtient des jetons (tokens) temporaires pour l'authentification à renvoyer avec un code PIN

        self.user_token = auth['oauth_token']
        self.user_secret = auth['oauth_token_secret']
        print(self.user_token)
        print(self.user_secret)
        self.auth_url = auth['auth_url']

    def final(self, oauth_verifier):
        # On demande des jetons permanents avec les jetons temporaires et le code PIN
        print("u" + self.user_token)
        print("s" + self.user_secret)
        print(self.app_token)
        print(self.app_secret)
        print("AH")
        co = Twython(self.app_token, self.app_secret, self.user_token, self.user_secret)

        final_step = co.get_authorized_tokens(oauth_verifier)

        print(final_step)

        return final_step


class Connec:
    def __init__(self, app_key, app_secret, user_key, user_secret):
        self.twython = Twython(app_key, app_secret, user_key, user_secret)
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
            print("Success!")
            print(cred)
        except TwythonError as e:
            print("Erreur: " + str(e))

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
        # TODO Fix debugrate
        # print(Connec.twitter)
        # print(twi)
        # print("x-rate-limit-limit:" + twi.get_lastfunction_header('x-rate-limit-limit'))
        # print("x-rate-limit-remaining: " + twi.get_lastfunction_header('x-rate-limit-remaining'))
        # print("x-rate-limit-reset: " + str(datetime.datetime.fromtimestamp(int(
        #     twi.get_lastfunction_header('x-rate-limit-reset')))))
        # print("H: " + str(datetime.datetime.now()))
