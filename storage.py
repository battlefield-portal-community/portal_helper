class Storage:
    def __init__(self):
        self.storage = dict()

    def add(self, dict_: dict):
        key = next(iter(dict_.keys()))
        if key in self.storage.keys():
            self.storage[key].add(dict_[key])
        else:
            self.storage[key] = [dict_[key]]

    def delete(self, key: int, value: None):
        if key in self.storage.keys() and value in self.storage[key]:
            self.storage[key].remove(value)
