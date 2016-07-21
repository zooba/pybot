from datetime import datetime
import json
import bot_requests

_STATE_URI = 'https://state.botframework.com'

class User:
    def __init__(self, state_uri, channel_id, conversation_id, data):
        self._state_uri = state_uri
        self._channel_id = channel_id
        self._conversation_id = conversation_id
        self._data = data
        self._id = data['id']
        self.name = data.get('name', '')
        self.data = {}
        self._etag = '*'
        self.conversation_data = {}
        self._conversation_etag = '*'
        self.reload_data()

    def save_data(self, include_data=True, include_conversation_data=True):
        if include_data:
            data = {'data': self.data, 'eTag': self._etag}
            bot_requests.set_user_data(self._state_uri, self._channel_id, self._id, data)
        if include_conversation_data:
            data = {'data': self.conversation_data, 'eTag': self._conversation_etag}
            bot_requests.set_private_conversation_data(self._state_uri, self._channel_id, self._conversation_id, self._id, data)

    def reload_data(self):
        data = bot_requests.get_user_data(self._state_uri, self._channel_id, self._id)
        self.data = data.get('data') or {}
        self._etag = data.get('eTag', '*')
        data = bot_requests.get_private_conversation_data(self._state_uri, self._channel_id, self._conversation_id, self._id)
        self.conversation_data = data.get('data') or {}
        self._conversation_etag = data.get('eTag', '*')

    def delete_data(self):
        bot_requests.delete_state_for_user(self._state_uri, self._channel_id, self._id)
        self.data = {}
        self._etag = '*'
        self.conversation_data = {}
        self._conversation_etag = '*'

class Message:
    def __init__(self, data):
        self.type = data['type']
        self.timestamp = data['timestamp']
        
        self._service_uri = data['serviceUrl']
        self._state_uri = self._service_uri if data['channelId'] == 'emulator' else _STATE_URI
        self._channel_id = data['channelId']
        self._conversation_id = data['conversation']['id']
        self._activity_id = data['id']

        self.conversation_name = data['conversation'].get('name', '')

        self.text = data.get('text', '')
        self.attachments = list(data.get('attachments', []))
        self.entities = list(data.get('entities', []))

        self.from_user = User(self._service_uri, self._channel_id, self._conversation_id, data['from'])
        self.recipient = User(self._service_uri, self._channel_id, self._conversation_id, data['recipient'])

        self.data = {}
        self._etag = '*'
        self.reload_data()

    def reload_data(self):
        data = bot_requests.get_conversation_data(self._state_uri, self._channel_id, self._conversation_id)
        self.data = data.get('data') or {}
        self._etag = data.get('eTag', '*')

    def save_data(self):
        data = {'data': self.data, 'eTag': self._etag}
        bot_requests.set_conversation_data(self._state_uri, self._channel_id, self._conversation_id, data)

    def post(self, text, attachments=[], entities=[], **extras):
        data = {
            'type': 'message',
            'conversation': {'id': self._conversation_id},
            **extras,
            'text': text
        }
        if attachments:
            data['attachments'] = [getattr(a, '_data', a) for a in attachments]
        if entities:
            data['entities'] = [getattr(e, '_data', e) for e in entities]
        bot_requests.send_to_conversation(self._service_uri, self._conversation_id, data)

    def reply(self, text, attachments=[], entities=[], **extras):
        data = {
            'type': 'message',
            'conversation': {'id': self._conversation_id},
            'replyToId': self._activity_id,
            'recipient': self.from_user._data,
            'from': self.recipient._data,
            **extras,
            'text': text,
        }
        if attachments:
            data['attachments'] = [getattr(a, '_data', a) for a in attachments]
        if entities:
            data['entities'] = [getattr(e, '_data', e) for e in entities]
        bot_requests.reply_to_activity(self._service_uri, self._conversation_id, self._activity_id, data)
