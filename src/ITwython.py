import datetime

from twython import *
from twython import TwythonStreamer


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
        # TODO Mettre try/except ?
        self.twython = Twython(app_key, app_secret, user_key, user_secret)
        # except AttributeError as e:
        #     print("Erreur ! Connexion impossible!")
        #     print(e)
        #     self.twython = None
        print("     " + str(self.twython))
        print("     " + str(self.twython.verify_credentials()))
        self._debugrate()

    def tweeter(self, message_du_tweet):
        try:
            cred = self.twython.update_status(status=message_du_tweet)
            print("Tweet envoyé : " + str(cred))
            self._debugrate()
            return True, "Tweet envoyé !"

        except TwythonError as e:
            print("Erreur envoi tweet : " + str(e))
            return False, str(e)

    # Underscore au début du nom -> convention pour fonction interne
    def _debugrate(self):
        """Affiche les infos sur les limites d'utilisation dans la console"""
        # J'ai "fixé" la fonction qui ne fait plus crasher et est plus propre : elle fait tjr la même chose
        print("Debugrate :\n  " + repr(self))

        a = self.twython.get_lastfunction_header('x-rate-limit-limit')
        b = self.twython.get_lastfunction_header('x-rate-limit-remaining')
        c = self.twython.get_lastfunction_header('x-rate-limit-reset')
        if a is not None:
            print("  x-rate-limit-limit:" + str(a))
        if b is not None:
            print("  x-rate-limit-remaining: " + str(b))
        if c is not None:
            print("  x-rate-limit-reset: " + str(datetime.datetime.fromtimestamp(int(c))))
            print("  H: " + str(datetime.datetime.now()))
        if a is None and b is None and c is None:
            print("  No header provided")

    def __repr__(self):
        return "<Connec : {0}>".format(self.twython)


class MyStreamer(TwythonStreamer):
    from main_app import TimeLine

    def __init__(self, app_key: str, app_secret: str, oauth_token: str, oauth_token_secret: str, timeline: TimeLine):
        TwythonStreamer.__init__(self, app_key, app_secret, oauth_token, oauth_token_secret)
        # On garde l'objet timeline pour pouvoir renvoyer les tweets à cet objet
        self.timeline = timeline

    def on_success(self, data):
        print(data)
        if 'text' in data:
            print(data["user"]["screen_name"], data["user"]["name"], data['text'], data["created_at"])
        self.timeline.add_data(data)

    def on_error(self, status_code, data):
        print(status_code)

        # Want to stop trying to get data because of the error?
        # Uncomment the next line!
        # self.disconnect()
