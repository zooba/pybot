import json

_SENTINEL = object()

def _wrap(cls, obj):
    if isinstance(obj, dict):
        return WrappedDict(obj)
    if isinstance(obj, (list, tuple)):
        return WrappedList(obj)
    return obj

class WrappedList:
    def __init__(self, d):
        self._d = d

    def __iter__(self):
        return map(_wrap, self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, index):
        return _wrap(self._d[index])

    def __setitem__(self, index, value):
        self._d[index] = value

    def __delitem__(self, index):
        del self._d[index]

class WrappedDict:
    def __init__(self, d):
        self._d = dict(d) if d else None

    def __getitem__(self, key):
        r = self.get(key, _SENTINEL)
        if r is _SENTINEL:
            raise KeyError(key)
        return self.wrap(r)

    def __setitem__(self, key, value):
        self._d[key] = value

    def __delitem__(self, key):
        del self._d[key]

    def get(self, key, default=None):
        if not self._d:
            return self

        r = self._d.get(key, _SENTINEL)
        if r is _SENTINEL:
            return default

        return _wrap(r)

    def __getattr__(self, attr):
        return _wrap(self.setdefault(attr, {}))

    def __setattr__(self, attr, value):
        self._d[attr] = value

    def __delattr__(self, attr):
        del self._d[attr]

    def __dir__(self):
        return list(self) + object.__dir__(self)

    def __iter__(self):
        return self._d

    def __len__(self):
        return len(self._d)

class Message:
    def __init__(self, data):
        self._data = dict(data)

    def respond(self, response):
        pass

    def to_json(self):
        return json.dumps(self._data)
