#-*- coding:utf-8 -*-
import Queue


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
            if q.full():
                q.get()
                q.put_nowait(val)
                return 1
        else:
            return self.set(key, val)

    def set(self, key, val):
        """Sets the `key` with `val`."""
        if isinstance(val, Queue.Queue):
            self.dictionary[key] = val
        else:
            q = Queue.Queue(self.__maxsize__)
            q.put_nowait(val)
            self.dictionary[key] = q
        return 1

    def get(self, key):
        """Retrieves a value of the `key` from the internal dictionary."""
        list_ = []
        try:
            q = self.dictionary[key]
            while not q.empty():
                list_.append(q.get_nowait())
        except KeyError:
            pass
        return list_

    def __repr__(self):
        modname = "" if __name__ == "__main__" else __name__ + "."
        return "<%s %r>" % (modname, self.dictionary)

notifications = Notification()