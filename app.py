import os
import sys
from bottle import get, post, request

if '--debug' in sys.argv[1:] or 'SERVER_DEBUG' in os.environ:
    # Debug mode will enable more verbose output in the console window.
    # It must be set at the beginning of the script.
    import bottle
    bottle.debug(True)

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
def root():
    msg = Message(request.json)

    if msg.type.lower() == 'ping':
        return

    if msg.type.lower() == 'message':
        return bot.on_message(msg)

    try:
        handler = getattr(bot, msg.type)
    except AttributeError:
        return {"message": "TODO: " + msg.type}
    else:
        return handler(msg)



if __name__ == '__main__':
    import bottle
    bottle.debug(True)

    # Starts a local test server.
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '3978'))
    except ValueError:
        PORT = 3978
    bottle.run(server='wsgiref', host=HOST, port=PORT)
else:
    import bottle

    wsgi_app = bottle.default_app()
