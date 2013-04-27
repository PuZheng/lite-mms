#-*- coding:utf-8 -*-
from collections import deque


class Notification(object):

    __slots__ = "dictionary",

    __maxsize__ = 5

    def __init__(self, *args, **kwargs):
        self.dictionary = {}
        if kwargs.has_key("maxsize"):
            self.__maxsize__ = int(kwargs.get("maxsize"))

    def delete(self, key):
        """Deletes the `key` from the dictionary."""
        if key in self.dictionary:
            del self.dictionary[key]
            return 1
        return 0

    def add(self, key, val):
        if key in self.dictionary:
            q = self.dictionary[key]
            q.appendleft(val)
        else:
            return self.set(key, val)

    def set(self, key, val):
        """Sets the `key` with `val`."""
        self.dictionary[key] = deque([val], maxlen=self.__maxsize__)
        return 1

    def get(self, key):
        """Retrieves a value of the `key` from the internal dictionary."""
        try:
            q = self.dictionary[key]
            return list(q)
        except KeyError:
            return []

    def __repr__(self):
        modname = "" if __name__ == "__main__" else __name__ + "."
        return "<%s %r>" % (modname, self.dictionary)

notifications = Notification()