
def on_message(msg):
    if msg.text.lower().startswith('call me '):
        msg.from_user.data['callme'] = msg.text[8:].strip()
        msg.from_user.save_data()
        msg.reply('Sure thing, ' + msg.from_user.data['callme'])
        return

    if msg.text.lower().startswith('i have a '):
        words = msg.text.split(' ')
        try:
            msg.from_user.data[' '.join(words[4:])] = words[3]
            msg.reply("Okay, I'll remember that.")
        except IndexError:
            msg.reply("You have a what now?")
        return

    if msg.text.lower() == 'what do you know about me':
        msg.reply('Just this:' + ', '.join('{}: {}'.format(*i) for i in msg.from_user.data.items()))
        return

    if msg.text.lower().startswith('hi'):
        callme = msg.from_user.data.get('callme')
        if callme:
            msg.reply('Hi, ' + callme + '!')
        else:
            msg.reply('Hi!')
        return

    msg.reply("Sorry, I don't understand that...")
