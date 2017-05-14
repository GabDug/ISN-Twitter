import datetime

from twython import *

import logger_conf

# from twython import TwythonStreamer

logger = logger_conf.Log.logger


# Modèles
class User:
    def __init__(self, data, *args, **kwargs):
        # logger.debug(str(data))
        # self.id = id
        # self.screen_name = screen_name
        self.id = data["id_str"]
        self.name = data["name"]
        self.screen_name = data["screen_name"]

        self.description = data["description"]
        self.location = data["location"]

        self.profile_image_url_normal = data["profile_image_url"]
        self.profile_image_url = self.profile_image_url_normal.replace("_normal", "")

        self.followers_count = data["followers_count"]
        self.friends_count = data["friends_count"]
        self.statuses_count = data["statuses_count"]
        try:
            self.profile_banner_url = data["profile_banner_url"]
        except KeyError as e:
            self.profile_image_url = None
            logger.error("Profile_banner_url : " + str(e))
            # TODO Ajouter tous les cas possibles et pas crasher si un élément pas présent


class Tweet:
    def __init__(self, data, *args, **kwargs):
        self.data = data
        self.created_at = data["created_at"]
        # TODO self.date = self.created_at mais en objet date
        self.id = data["id_str"]
        self.text = data["text"]
        self.user = User(data["user"])

        self.favorited = data["favorited"]
        self.retweeted = data["retweeted"]

        self.retweet_count = data["retweet_count"]
        self.favorite_count = data["favorite_count"]


# Connections
class ConnecTemporaire:
    def __init__(self, _app_token, _app_secret):
        self.app_token = _app_token
        self.app_secret = _app_secret
        logger.debug("Temp App Token          : " + self.app_token)
        logger.debug("Temp App Token Secret   : " + self.app_secret)

        self.connection = Twython(self.app_token, self.app_secret)
        auth = self.connection.get_authentication_tokens()
        # On obtient des jetons (tokens) temporaires pour l'authentification à renvoyer avec un code PIN

        self.user_token = auth['oauth_token']
        self.user_secret = auth['oauth_token_secret']
        logger.debug("Temp OAuth Token        : " + self.user_token)
        logger.debug("Temp OAuth Token Secret : " + self.user_secret)

        self.auth_url = auth['auth_url']
        logger.debug("Lien de connexion       :" + self.auth_url)

    def final(self, oauth_verifier):
        # On demande des jetons permanents avec les jetons temporaires et le code PIN
        logger.debug("App Token         : " + self.app_token)
        logger.debug("App Token Secret  : " + self.app_secret)
        logger.debug("User Token        : " + self.user_token)
        logger.debug("User Token Secret : " + self.user_secret)
        co = Twython(self.app_token, self.app_secret, self.user_token, self.user_secret)

        try:
            final_step_dic = co.get_authorized_tokens(oauth_verifier)
            logger.debug("Final Step :" + str(final_step_dic))
            return True, final_step_dic
        except TwythonError as e:
            logger.debug("Erreur Twython : " + e)
            return False, str(e)


class Connec(Twython):
    def __init__(self, app_key, app_secret, user_key, user_secret, real=True):
        if real:
            try:
                Twython.__init__(self, app_key, app_secret, user_key, user_secret)
                cred = self.verify_credentials()
                logger.debug(str(cred).encode("utf-8").decode("utf-8"))
                self.user = User(cred)
                self._debugrate()
                self.exist = True
                self.fake = False
                self.erreur = None
            except TwythonError as e:
                if str(e) == "Twitter API returned a 401 (Unauthorized), Invalid or expired token.":
                    logger.error("Token invalide ou expiré ! Erreur : " + str(e))
                    self.erreur = "token_invalid"
                elif str(e) == "Twitter API returned a 400 (Bad Request), Bad Authentication data.":
                    logger.error("Jetons incorrects ! Erreur : " + str(e))
                    self.erreur = "app_token_invalid"
                else:
                    logger.error("Impossible de créer la connection Twython ! Erreur : " + str(e))
                    self.erreur = True
                self.exist = False
                return
        else:
            logger.warning("Debug : Connexion non créée.")
            self.exist = True
            self.fake = True
            self.erreur = None
            return
        # TODO Mettre try/except ?
        self.twython = self
        # except AttributeError as e:
        #     logger.debug("Erreur ! Connexion impossible!")
        #     logger.debug(e)
        #     self.twython = None
        logger.debug("     " + str(self))

    def tweeter(self, message_du_tweet):
        if not self.fake:
            try:
                cred = self.update_status(status=message_du_tweet)
                logger.debug("TweetGUI envoyé : " + str(cred))
                self._debugrate()
                return True, "TweetGUI envoyé !"

            except TwythonError as e:
                logger.debug("Erreur envoi tweet : " + str(e))
                return False, str(e)
        else:
            return True, "Fake tweet envoyé !"

    def fav(self, id: str):
        self.create_favorite(id=id)

    def defav(self, id: str):
        pass

    # on ne peux pas appeler la fonction retweet car une fonction de Twython existe déjà
    def retweeter(self, id: str):
        self.retweet(id=id)

    def unretweeter(self, id: str):
        # Je crois qu'il faut supprimer un tweet pour unretweet
        pass
        # annuler le retweet

    def reply(self, id: str):
        # TODO fonction pour ouvrir fenêtre de réponse à 1 utilisateur (On va réutiliser tweeter et pas faire reply)
        pass

    # Underscore au début du nom -> convention pour fonction interne
    def _debugrate(self):
        """Affiche les infos sur les limites d'utilisation dans la console"""
        # J'ai "fixé" la fonction qui ne fait plus crasher et est plus propre : elle fait tjr la même chose
        logger.debug("Debugrate : " + repr(self))

        a = self.get_lastfunction_header('x-rate-limit-limit')
        b = self.get_lastfunction_header('x-rate-limit-remaining')
        c = self.get_lastfunction_header('x-rate-limit-reset')
        if a is not None:
            logger.debug("  x-rate-limit-limit:" + str(a))
        if b is not None:
            logger.debug("  x-rate-limit-remaining: " + str(b))
        if c is not None:
            logger.debug("  x-rate-limit-reset: " + str(datetime.datetime.fromtimestamp(int(c))))
            logger.debug("  H: " + str(datetime.datetime.now()))
        if a is None and b is None and c is None:
            logger.debug("  No header provided")

            # def __repr__(self):
            #     return "<Connec : {0}>".format(self)


class MyStreamer(TwythonStreamer):
    def __init__(self, timeline, *args, **kwargs):
        TwythonStreamer.__init__(self, *args, **kwargs)

        # On garde l'objet timeline pour pouvoir renvoyer les tweets à cet objet
        self.timeline = timeline

    # Fonctions lancées à la réception d'informations (succès ou échec)
    def on_success(self, data):
        logger.debug(data)
        if 'text' in data:
            try:
                logger.debug(data["user"]["screen_name"].encode("utf-8"), data["user"]["name"].encode("utf-8"),
                             data['text'].encode("utf-8"), data["created_at"].encode("utf-8"))
            except TypeError as e:
                logger.error(e)

        self.timeline.add_data(data)

    def on_error(self, status_code, data):
        logger.error("Erreur ! " + status_code)

        # On peut se déconnecter après une erreur
        # self.disconnect()
