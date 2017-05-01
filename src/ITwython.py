import datetime

from twython import *
from twython import TwythonStreamer

import logger_conf

logger = logger_conf.Log.logger


# Modèles
class User:
    def __init__(self, data, *args, **kwargs):
        # self.id = id
        # self.screen_name = screen_name
        self.id = data["id_str"]
        self.name = data["name"]
        self.screen_name = data["screen_name"]

        self.profile_image_url = data["profile_image_url"]
        # TODO Ajouter tous les cas possibles et pas crasher si un élément pas présent
        # {'id': 2862904287, 'id_str': '2862904287', 'name': 'nullos 1er', 'screen_name': 'DUGNYCHON', 'location': 'ahhh', 'description': 'aaaaaaahhhhh.......', 'url': None, 'entities': {'description': {'urls': []}}, 'protected': False, 'followers_count': 206, 'friends_count': 208, 'listed_count': 2, 'created_at': 'Wed Nov 05 18:04:48 +0000 2014', 'favourites_count': 5252, 'utc_offset': 7200, 'time_zone': 'Paris', 'geo_enabled': True, 'verified': False, 'statuses_count': 9956, 'lang': 'fr', 'status': {'created_at': 'Sun Apr 16 18:56:36 +0000 2017', 'id': 853683561794326528, 'id_str': '853683561794326528', 'text': 'bonjour', 'truncated': False, 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': []}, 'source': '<a href="https://github.com/SoFolichon/ISN-Twitter" rel="nofollow">ISNProject</a>', 'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None, 'in_reply_to_user_id': None, 'in_reply_to_user_id_str': None, 'in_reply_to_screen_name': None, 'geo': None, 'coordinates': None, 'place': None, 'contributors': None, 'is_quote_status': False, 'retweet_count': 0, 'favorite_count': 0, 'favorited': False, 'retweeted': False, 'lang': 'fr'}, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': '000000', 'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_tile': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/852591994614558722/WfKXBaed_normal.jpg', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/852591994614558722/WfKXBaed_normal.jpg', 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/2862904287/1491862723', 'profile_link_color': '000000', 'profile_sidebar_border_color': '000000', 'profile_sidebar_fill_color': '000000', 'profile_text_color': '000000', 'profile_use_background_image': False, 'has_extended_profile': True, 'default_profile': False, 'default_profile_image': False, 'following': False, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'regular'}


class Tweet:
    def __init__(self, data, *args, **kwargs):
        self.data = data
        self.created_at = data["created_at"]
        # TODO self.date = self.created_at mais en objet date
        self.id = data["id"]
        self.id_str = data["id_str"]
        self.text = data["text"]
        self.user = User(data["user"])


# Connections
class ConnecTemporaire:
    def __init__(self, _app_token, _app_secret):
        self.app_token = _app_token
        self.app_secret = _app_secret
        logger.debug(self.app_token)
        logger.debug(self.app_secret)

        self.connection = Twython(self.app_token, self.app_secret)
        auth = self.connection.get_authentication_tokens()
        # On obtient des jetons (tokens) temporaires pour l'authentification à renvoyer avec un code PIN

        self.user_token = auth['oauth_token']
        self.user_secret = auth['oauth_token_secret']
        logger.debug(self.user_token)
        logger.debug(self.user_secret)
        self.auth_url = auth['auth_url']

    def final(self, oauth_verifier):
        # On demande des jetons permanents avec les jetons temporaires et le code PIN
        logger.debug(" User token : " + self.user_token)
        logger.debug(" User secret token : " + self.user_secret)
        logger.debug(" App token : " + self.app_token)
        logger.debug(" App token : " + self.app_secret)
        co = Twython(self.app_token, self.app_secret, self.user_token, self.user_secret)

        try:
            final_step = co.get_authorized_tokens(oauth_verifier)
            logger.debug(final_step)
            return True, final_step
        except TwythonError as e:
            logger.debug(e)
            return False, str(e)


class Connec(Twython):
    def __init__(self, app_key, app_secret, user_key, user_secret, real=True):
        if real:
            try:
                Twython.__init__(self, app_key, app_secret, user_key, user_secret)
                cred = self.verify_credentials()
                # logger.debug(str(cred).encode("utf-8").decode("utf-8"))
                self.user = User(cred)
                self._debugrate()
                self.exist = True
                self.fake = False
            except TwythonError as e:
                logger.error("Impossible de créer la connection Twython ! Erreur : " + str(e))
                self.exist = False
                return
        else:
            logger.warning("Connexion non créée")
            self.exist = True
            self.fake = True
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
        logger.error("Erreur ! "+status_code)

        # Want to stop trying to get data because of the error?
        # Uncomment the next line!
        # self.disconnect()
