import os
from bottle import get, post, request, auth_basic
from pprint import pprint

APP_ID = os.getenv("APP_ID", "YourAppId")
APP_SECRET = os.getenv("APP_SECRET", "YourAppSecret")

def check_auth(id, secret):
    return id == APP_ID and secret == APP_SECRET

import builtins
import math
CALC_ENV = {}
CALC_ENV.update({k: getattr(builtins, k) for k in dir(builtins)})
CALC_ENV.update({k: getattr(math, k) for k in dir(math)})

class Conversation:
    def __init__(self, id):
        self.id = id
        self.history = []

    def fallback(self, msg):
        pprint(msg)
        return "Unknown message type {[type]}".format(msg)

    def BotAddedToConversation(self, msg):
        return "Welcome to the conversation, {[mentions][0][text]}!".format(msg)

    def UserAddedToConversation(self, msg):
        return "Hi {[mentions][0][text]}! Glad you could make it!".format(msg)

    def Message(self, msg):
        try:
            key, _, text = msg['text'].partition(' ')
            return getattr(self, "Message_" + key.lower())(msg, text)
        except:
            return "Sorry {[from][name]}, I didn't understand that.".format(msg)

    def Message_calculate(self, msg, text):
        try:
            env = dict(CALC_ENV)
            return "Looks like that equals {}".format(eval(text, env, {}))
        except:
            return "Sorry {[from][name]}, I couldn't calculate that.".format(msg)
        
    def Message_history(self, msg, text):
        return "Here's what you've told me recently:\r\n{}".format('\r\n'.join(m['text'] for m in self.history))

CONVERSATIONS = {}

@post('/api/messages')
@auth_basic(check_auth)
def root():
    msg = dict(request.json)
    
    c_id = msg['conversationId']
    conv = CONVERSATIONS.get(c_id)
    if not conv:
        CONVERSATIONS[c_id] = conv = Conversation(c_id)

    conv.history.append(msg)
    res = getattr(conv, msg['type'], conv.fallback)(msg)

    if isinstance(res, str):
        return {'text': res}
    return res
