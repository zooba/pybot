
class Attachment:
    def __init__(self, content_type, content_url, name, thumbnail_url=None, content=None):
        self._data = {
            "contentType": content_type,
            "contentUrl": content_url,
            "name": name,
        }
        if content:
            self._data["content"] = content
        if thumbnail_url:
            self._data["thumbnailUrl"] = thumbnail_url

    @property
    def content_type(self):
        return self._data["contentType"]

    @content_type.setter
    def content_type(self, value):
        self._data["contentType"] = value

    @property
    def content_url(self):
        return self._data["contentUrl"]

    @content_type.setter
    def content_url(self, value):
        self._data["contentUrl"] = value

    @property
    def name(self):
        return self._data["name"]

    @name.setter
    def name(self, value):
        self._data["name"] = value
