import os
import sys
from bottle import get, post, request, auth_basic

if '--debug' in sys.argv[1:] or 'SERVER_DEBUG' in os.environ:
    # Debug mode will enable more verbose output in the console window.
    # It must be set at the beginning of the script.
    import bottle
    bottle.debug(True)

APP_ID = os.getenv("APP_ID", "YourAppId")
APP_SECRET = os.getenv("APP_SECRET", "YourAppSecret")

def check_auth(id, secret):
    return id == APP_ID and secret == APP_SECRET

from message import Message
import bot

@get('/')
def home():
    try:
        bot.home
    except AttributeError:
        pass
    else:
        return bot.home()
    
    return "TODO: home page"

@post('/api/messages')
#@auth_basic(check_auth)
def root():
    msg = Message(request.json)

    try:
        handler = getattr(bot, msg.type)
    except AttributeError:
        res = "TODO: " + msg.type
    else:
        res = handler(msg)

    if isinstance(res, str):
        return {'text': res}
    return res



if __name__ == '__main__':
    import bottle

    # Starts a local test server.
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    bottle.run(server='wsgiref', host=HOST, port=PORT)
else:
    import bottle

    wsgi_app = bottle.default_app()
