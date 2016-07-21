import json
from base64 import b64encode
import requests
import os

from datetime import datetime, timedelta

_AUTH_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
_AUTH_SCOPE = 'https://graph.microsoft.com/.default'
APP_ID = os.getenv('APP_ID')
APP_PASSWORD = os.getenv('APP_PASSWORD')

class _BotSession:
    def __init__(self, auth_url, auth_scope, app_id, app_password):
        self.auth_url = auth_url
        self.auth_scope = auth_scope
        self.app_id = app_id
        self.app_password = app_password
        
        self._session = None
        self._token = None
        self._token_expires_at = datetime.utcnow()

    def _refresh_token(self):
        r = requests.post(self.auth_url, data={
            'grant_type': 'client_credentials',
            'client_id': self.app_id,
            'client_secret': self.app_password,
            'scope': self.auth_scope,
        })
        self._token = _raise_or_get_json(r)
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=int(self._token.get('expires_in', 3600)))

    def get(self):
        if self._token_expires_at < datetime.utcnow():
            if self._session:
                self._session.close()
                self._session = None
            self._refresh_token()
        if not self._session:
            self._session = requests.Session()
            self._session.headers['Authorization'] = '{0[token_type]} {0[access_token]}'.format(self._token)
        return self._session

class _EmulatorSession:
    def __init__(self):
        self._session = requests.Session()

    def get(self):
        return self._session

if not APP_ID:
    _session = _EmulatorSession()
else:
    _session = _BotSession(_AUTH_URL, _AUTH_SCOPE, APP_ID, APP_PASSWORD)

def _join(*parts):
    return '/'.join(p.rstrip('/') for p in parts)

def _raise_or_get_json(response):
    if response.status_code == 403:
        print(response.request.headers)
        print(response.headers)
    
    try:
        response.raise_for_status()
    except Exception:
        try:
            data = response.json()
        except Exception:
            pass
        else:
            if 'message' in data:
                # Chain the exception with more specific info
                # TODO: Better exception type here
                raise Exception(data['message'])
            raise
    try:
        return response.json()
    except json.JSONDecodeError:
        return {}

#region BotState API

def delete_state_for_user(state_uri, channel_id, user_id):
    r = _session.get().delete(
        _join(state_uri, 'v3', 'botstate', channel_id, 'users', user_id),
    )
    _raise_or_get_json(r)

def get_user_data(state_uri, channel_id, user_id):
    r = _session.get().get(
        _join(state_uri, 'v3', 'botstate', channel_id, 'users', user_id),
        headers={'Accept': 'application/json'},
    )
    return _raise_or_get_json(r)

def set_user_data(state_uri, channel_id, user_id, etag_and_data):
    r = _session.get().post(
        _join(state_uri, 'v3', 'botstate', channel_id, 'users', user_id),
        json=etag_and_data,
        headers={'Accept': 'application/json'},
    )
    return _raise_or_get_json(r)

def get_conversation_data(state_uri, channel_id, conversation_id):
    r = _session.get().get(
        _join(state_uri, 'v3', 'botstate', channel_id, 'conversations', conversation_id),
        headers={'Accept': 'application/json'},
    )
    return _raise_or_get_json(r)

def set_conversation_data(state_uri, channel_id, conversation_id, etag_and_data):
    r = _session.get().post(
        _join(state_uri, 'v3', 'botstate', channel_id, 'conversations', conversation_id),
        json=etag_and_data,
        headers={'Accept': 'application/json'},
    )
    return _raise_or_get_json(r)

def get_private_conversation_data(state_uri, channel_id, conversation_id, user_id):
    r = _session.get().get(
        _join(state_uri, 'v3', 'botstate', channel_id, 'conversations', conversation_id, 'users', user_id),
        headers={'Accept': 'application/json'},
    )
    return _raise_or_get_json(r)

def set_private_conversation_data(state_uri, channel_id, conversation_id, user_id, etag_and_data):
    r = _session.get().post(
        _join(state_uri, 'v3', 'botstate', channel_id, 'conversations', conversation_id, 'users', user_id),
        json=etag_and_data,
        headers={'Accept': 'application/json'},
    )
    return _raise_or_get_json(r)

#endregion

#region BotConnector Attachment API

def get_attachment_info(service_uri, attachment_id):
    r = _session.get().get(
        _join(service_uri, 'v3', 'attachments', attachment_id),
        headers={'Accept': 'application/json'},
    )
    return _raise_or_get_json(r)

def get_attachment(service_uri, attachment_id, view_id):
    r = _session.get().get(
        _join(service_uri, 'v3', 'attachments', attachment_id, 'views', view_id),
        headers={'Accept': 'application/json'},
    )
    return _raise_or_get_json(r)

#endregion

#region BotConnector API

def create_conversation(service_uri, topic_name, bot_id, bot_name, member_id_name_pairs):
    r = _session.get().post(
        _join(service_uri, 'v3', 'conversations'),
        headers={'Accept': 'application/json'},
        json={
            'topicName': topic_name,
            'bot': { 'id': bot_id, 'name': bot_name },
            'members': [{'id': id, 'name': name} for id, name in member_id_name_pairs]
        }
    )
    return _raise_or_get_json(r)

def send_to_conversation(service_uri, conversation_id, activity):
    r = _session.get().post(
        _join(service_uri, 'v3', 'conversations', conversation_id, 'activities'),
        headers={'Accept': 'application/json'},
        json=activity,
    )
    return _raise_or_get_json(r)

def reply_to_activity(service_uri, conversation_id, activity_id, activity):
    r = _session.get().post(
        _join(service_uri, 'v3', 'conversations', conversation_id, 'activities', activity_id),
        headers={'Accept': 'application/json'},
        json=activity,
    )
    return _raise_or_get_json(r)

def get_conversation_members(service_uri, conversation_id):
    r = _session.get().get(
        _join(service_uri, 'v3', 'conversations', conversation_id, 'members'),
        headers={'Accept': 'application/json'},
    )
    return _raise_or_get_json(r)

def get_activity_members(service_uri, conversation_id, activity_id):
    r = _session.get().get(
        _join(service_uri, 'v3', 'conversations', conversation_id, 'activities', activity_id, 'members'),
        headers={'Accept': 'application/json'},
    )
    return _raise_or_get_json(r)

def upload_attachment(service_uri, conversation_id, type, name, data_bytes, thumbnail_data_bytes=None):
    data = {
        'type': type,
        'name': name,
        'originalBase64': b64encode(data_bytes).decode(),
    }
    if thumbnail_data:
        data['thumbnailBase64'] = b64encode(thumbnail_data_bytes).decode()
    
    r = _session.get().post(
        _join(service_uri, 'v3', 'conversations', conversation_id, 'attachments'),
        headers={'Accept': 'application/json'},
        json=data,
    )
    return _raise_or_get_json(r)

#endregion

