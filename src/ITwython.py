# -*- coding: utf-8 -*-

import re
from datetime import datetime
from datetime import timezone

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
        self.name = re.sub(u'[\u263a-\U0001f645]', '\u2610', data["name"]).encode("utf-8").decode('utf-8')
        self.screen_name = re.sub(u'[\u263a-\U0001f645]', '\u2610', data["screen_name"]).encode("utf-8").decode('utf-8')

        self.description = re.sub(u'[\u263a-\U0001f645]', '\u2610', data["description"]).encode("utf-8").decode('utf-8')
        self.location = re.sub(u'[\u263a-\U0001f645]', '\u2610', data["location"]).encode("utf-8").decode('utf-8')

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
        self.date = (datetime.strptime(self.created_at, '%a %b %d %H:%M:%S %z %Y').replace(
            tzinfo=timezone.utc).astimezone(tz=None).strftime('Le %d/%m/%Y à %H:%M:%S'))
        # TODO self.date = self.created_at mais en objet date
        self.id = data["id_str"]
        # self.text = data["text"]
        self.text = re.sub(u'[\u263a-\U0001ffff]+', '\u2610', data["text"])
        # logger.warning(self.text)
        self.user = User(data["user"])

        self.favorited = data["favorited"]
        self.retweeted = data["retweeted"]

        self.retweet_count = data["retweet_count"]
        self.favorite_count = data["favorite_count"]


# Connections
class ConnexionTemporaire:
    """Objet qui crée une connexion twython temporaire, utilisé à la première connexion pour récupérer les jetons 
    définitifs."""

    def __init__(self, _app_token, _app_secret):
        self.app_token = _app_token
        self.app_secret = _app_secret
        # logger.debug("Temp App Token          : " + self.app_token)
        # logger.debug("Temp App Token Secret   : " + self.app_secret)

        # On crée une connexion Twython avec Twitter, mais sans utilisateur spécifique
        self.connexion = Twython(self.app_token, self.app_secret)
        # On obtient des jetons (tokens) temporaires avec un lien pour s'authentifier
        auth = self.connexion.get_authentication_tokens()

        self.user_token = auth['oauth_token']
        self.user_secret = auth['oauth_token_secret']
        logger.debug("Temp OAuth Token        : " + self.user_token)
        logger.debug("Temp OAuth Token Secret : " + self.user_secret)

        self.auth_url = auth['auth_url']
        logger.debug("Lien de connexion       :" + self.auth_url)

    def final(self, oauth_verifier):
        """Permet de récupérer des jetons définitifs avec des jetons temporaires et le code obtenu sur la page web."""
        # On demande des jetons permanents avec les jetons temporaires et le code PIN
        # logger.debug("App Token         : " + self.app_token)
        # logger.debug("App Token Secret  : " + self.app_secret)
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


class Connexion(Twython):
    """Classe qui hérite de Twython, ajoute des vérifications et gère les erreurs. Gère la RestAPI de Twitter."""

    def __init__(self, app_key, app_secret, user_key, user_secret, real=True):
        # Si le programme n'est pas en debug
        if real:
            try:
                Twython.__init__(self, app_key, app_secret, user_key, user_secret)
                cred = self.verify_credentials()
                # logger.debug("Credentials : " + str(cred).encode("utf-8").decode("utf-8"))

                # L'utilisateur qui s'est connecté
                self.user = User(cred)
                self._debugrate()
                self.existe = True
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
                    logger.error("Impossible de créer la connexion Twython ! Erreur : " + str(e))
                    self.erreur = True
                self.existe = False
                return
        else:
            logger.warning("Debug : Connexion non créée.")
            self.existe = True
            self.fake = True
            self.erreur = None
            return
        # TODO Mettre try/except ?
        # TODO vérifier si l'attribut .twython peut être supprimé
        self.twython = self
        # except AttributeError as e:
        #     logger.debug("Erreur ! Connexion impossible!")
        #     logger.debug(e)
        #     self.twython = None
        logger.debug("     " + str(self))

    def tweeter(self, message_du_tweet, reponse=None):
        """Fonction pour envoyer un tweet (status)."""
        # Si on n'est pas en debug
        if not self.fake:
            try:
                if reponse is None:
                    logger.debug("Reponse None")
                    cred = self.update_status(status=message_du_tweet)
                else:
                    logger.debug("Reponse à + " + reponse)
                    cred = self.update_status(status=message_du_tweet, in_reply_to_status_id=reponse)
                logger.debug("Tweet envoyé : " + str(cred))
                self._debugrate()
                return True, "Tweet envoyé !"

            except TwythonError as e:
                logger.debug("Erreur envoi tweet : " + str(e))
                return False, str(e)
        else:
            return True, "Fake tweet envoyé !"

    def respond(self, message_du_tweet):
        """Fonction pour envoyer un tweet (status)."""
        # Si on n'est pas en debug
        if not self.fake:
            try:
                cred = self.update_status(status=message_du_tweet, in_reply_to_status_id=Tweet["id"])
                logger.debug("Tweet envoyé : " + str(cred))
                self._debugrate()
                return True, "Tweet envoyé !"

            except TwythonError as e:
                logger.debug("Erreur envoi tweet : " + str(e))
                return False, str(e)
        else:
            return True, "Fake tweet envoyé !"

    def fav(self, id_tweet: str):
        self.create_favorite(id=id_tweet)

    def defav(self, id_tweet: str):
        self.destroy_favorite(id=id_tweet)

    # On ne peux pas appeler la fonction retweet car une fonction de Twython existe déjà (risque d'override)
    def retweeter(self, id_tweet: str):
        self.retweet(id=id_tweet)

    # TODO finir
    # def Respond(self, tweet : Tweet):
    #    #name = Tweet["user"]["screen_name"]
    #    #text = self.parent.EnvoiTweet()
    #    msg = input("enter msg here")
    #    text = " ".join(msg)
    #    credo = self.update_status(status=text, in_reply_to_status_id=Tweet["id"])
    #    logger.debug("Tweet envoyé : " + str(credo))
    #    self._debugrate()
    #    return True, "Tweet envoyé !"

    def reply(self, id_tweet: str):
        # TODO fonction pour ouvrir fenêtre de réponse à 1 utilisateur (On va réutiliser tweeter et pas faire reply)
        pass

    # Underscore au début du nom -> convention pour fonction interne
    def _debugrate(self):
        """Affiche les infos sur les limites d'utilisation dans la console."""
        logger.debug("Debugrate : " + repr(self))

        a = self.get_lastfunction_header('x-rate-limit-limit')
        b = self.get_lastfunction_header('x-rate-limit-remaining')
        c = self.get_lastfunction_header('x-rate-limit-reset')
        if a is not None:
            logger.debug("  x-rate-limit-limit:" + str(a))
        if b is not None:
            logger.debug("  x-rate-limit-remaining: " + str(b))
        if c is not None:
            logger.debug("  x-rate-limit-reset: " + str(datetime.fromtimestamp(int(c))))
            logger.debug("  H: " + str(datetime.now()))
        if a is None and b is None and c is None:
            logger.debug("  No header provided")


class ConnexionStream(TwythonStreamer):
    """Classe qui hérite de la connexion TwythonStreamer : se connecte à la Stream API de Twitter pour récupérer
     les tweets en direct."""

    def __init__(self, timeline, *args, **kwargs):
        TwythonStreamer.__init__(self, *args, **kwargs)

        # On garde l'objet timeline pour pouvoir renvoyer les tweets à cet objet
        self.timeline = timeline

    # Fonction appelée lors de la réception avec succès d'un message (Tweet ou demande de suppresion d'un tweet)
    def on_success(self, data):
        # try:
        #     logger.debug(str(repr(data)))
        # except UnicodeEncodeError:
        #     pass
        # if 'text' in data:
        #     try:
        #         logger.debug(data["user"]["screen_name"].encode("utf-8"), data["user"]["name"].encode("utf-8"),
        #                      data['text'].encode("utf-8"), data["created_at"].encode("utf-8"))
        #     except TypeError as e:
        #         logger.error(e)

        self.timeline.add_data(data)

    # Fonction appelée lors d'une erreur
    def on_error(self, status_code, data):
        logger.error("Erreur ! " + status_code)

        # Fonction appelée si timeout des requêtes
        # def on_timeout(self):
        #     pass

        # On peut se déconnecter après une erreur ou un timeout
        # self.disconnect()
