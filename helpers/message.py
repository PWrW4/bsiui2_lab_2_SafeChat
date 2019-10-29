import json


def create_message(action, arg1=None, arg2=None):
    def convert(a):
        it = iter(a)
        res_dct = dict(zip(it, it))
        return res_dct

    list = []
    if action == "M" or action == "ERROR":
        list = ["action", action, "message", str(arg1)]
    elif action == "L" or action == "R":
        list = ["action", action, "login", str(arg1), "password", str(arg2)]
    elif action == "OK" or action == "HELLO":
        list = ["action", action]
    else:
        return "ERROR - action not found"
    json_msg = json.dumps(convert(list)) + "\n"
    return json_msg.encode(encoding='utf-8')


def measage_to_json(msg):
    return json.loads(msg)
