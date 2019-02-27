import json


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def get_credential(key):
    return json.load(open('./credentials.json'))[key]
