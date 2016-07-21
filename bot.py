
def on_message(msg):
    if msg.text.lower().startswith('call me '):
        msg.from_user.data['callme'] = msg.text[8:].strip()
        msg.from_user.save_data()
        msg.reply('Sure thing, ' + msg.from_user.data['callme'])
        return
    
    if msg.text.lower() == 'what do you know about me':
        msg.reply('\r\n'.join(['Just this:'] + ['*{}*: {}'.format(*i) for i in msg.from_user.data.items()]))
        return

    if msg.text.lower().startswith('hi'):
        callme = msg.from_user.data.get('callme')
        if callme:
            msg.reply('Hi, ' + callme + '!')
        else:
            msg.reply('Hi!')
        return

    msg.reply("Sorry, I don't understand that...")
