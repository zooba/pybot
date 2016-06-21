import builtins
import math
CALC_ENV = {}
CALC_ENV.update({k: getattr(builtins, k) for k in dir(builtins)})
CALC_ENV.update({k: getattr(math, k) for k in dir(math)})

def BotAddedToConversation(msg):
    return "Welcome to the conversation, {0.mentions[0].text}!".format(msg)

def UserAddedToConversation(msg):
    return "Hi {.mentions[0].text}! Glad you could make it!".format(msg)

def Message(msg):
    key, _, text = msg.text.partition(' ')
    if key == 'calculate:
        try:
            env = dict(CALC_ENV)
            return "Looks like that equals {}".format(eval(text, env, {}))
        except:
            return "Sorry {.from.name}, I couldn't calculate that.".format(msg)
    
    return "Sorry {.from.name}, I didn't understand that.".format(msg)
