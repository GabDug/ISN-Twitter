from secrets import TWITTER_APP_KEY, TWITTER_APP_SECRET

from twython import Twython

APP_KEY = TWITTER_APP_KEY
APP_SECRET = TWITTER_APP_SECRET

# On demande à Twitter d'identifier...
twitter = Twython(APP_KEY, APP_SECRET)
auth = twitter.get_authentication_tokens()

# On obtient des jetons (tokens) temporaires pour l'authentification à renvoyer avec un code PIN
OAUTH_TOKEN = auth['oauth_token']
OAUTH_TOKEN_SECRET = auth['oauth_token_secret']
print("Accédez à cet url : " + auth['auth_url'])
oauth_verifier = input("Code PIN ? ")

# On demande des jetons permanents avec les jetons temporaires et le code PIN
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

final_step = twitter.get_authorized_tokens(oauth_verifier)

# TODO Sauvegarder les jetons permanents pour se reconnecter, dans secrets.py ?

print(final_step)
