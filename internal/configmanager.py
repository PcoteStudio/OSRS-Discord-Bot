import json

instance = None


def init(filename, encoding):
    global instance
    with open(filename, 'r', encoding=encoding) as doc:
        instance = json.load(doc)
