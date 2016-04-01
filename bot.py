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

class MessageList:
    def __init__(self, d):
        self._d = d

    def __getitem__(self, index):
        return Message.wrap(self._d[index])

class Message:
    _sentinel = object()

    @classmethod
    def wrap(cls, obj):
        if isinstance(obj, dict):
            return cls(obj)
        if isinstance(obj, (list, tuple)):
            return MessageList(obj)
        return obj

    def __init__(self, d):
        self._d = dict(d) if d else None

    def __getitem__(self, key):
        r = self.get(key, self._sentinel)
        if r is self._sentinel:
            raise KeyError(key)
        return self.wrap(r)

    def get(self, key, default=None):
        if not self._d:
            return self

        r = self._d.get(key, self._sentinel)
        if r is self._sentinel:
            return default

        return self.wrap(r)

    def __getattr__(self, attr):
        r = self.get(attr, self._sentinel)
        if r is self._sentinel:
            return Message(None)
        return self.wrap(r)

class Conversation:
    def __init__(self, id):
        self.id = id
        self.history = []

    def fallback(self, msg):
        pprint(msg)
        return "Unknown message type {[type]}".format(msg)

    def BotAddedToConversation(self, msg):
        return "Welcome to the conversation, {0.mentions[0].text}!".format(msg)

    def UserAddedToConversation(self, msg):
        return "Hi {.mentions[0].text}! Glad you could make it!".format(msg)

    def Message(self, msg):
        try:
            key, _, text = msg.text.partition(' ')
            return getattr(self, "Message_" + key.lower())(msg, text)
        except:
            return "Sorry {.from.name}, I didn't understand that.".format(msg)

    def Message_calculate(self, msg, text):
        try:
            env = dict(CALC_ENV)
            return "Looks like that equals {}".format(eval(text, env, {}))
        except:
            return "Sorry {.from.name}, I couldn't calculate that.".format(msg)
        
    def Message_history(self, msg, text):
        return "Here's what you've told me recently:\r\n{}".format('\r\n'.join(m.text for m in self.history))

CONVERSATIONS = {}

@post('/api/messages')
#@auth_basic(check_auth)
def root():
    msg = Message(request.json)
    
    c_id = msg.conversationId
    conv = CONVERSATIONS.get(c_id)
    if not conv:
        CONVERSATIONS[c_id] = conv = Conversation(c_id)

    conv.history.append(msg)
    conv.Message_calculate
    res = getattr(conv, msg.type, conv.fallback)(msg)

    if isinstance(res, str):
        return {'text': res}
    return res
