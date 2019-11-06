import json


def create_message(action: str, arg1=None, arg2=None, arg3=None):
    def convert(a):
        it = iter(a)
        res_dct = dict(zip(it, it))
        return res_dct

    lst = []
    if action == "M" or action == "ERROR" or action == "CT":
        lst = ["action", action, "message", str(arg1)]
    elif action == "L" or action == "R":
        lst = ["action", action, "login", str(arg1), "password", str(arg2), "port", str(arg2)]
    elif action == "UU":
        lst = ["action", action, "ulist", list(arg1)]
    elif action == "OK" or action == "HELLO" or action == "OUT":
        lst = ["action", action]
    else:
        return "ERROR - action not found"
    json_msg = json.dumps(convert(lst))
    return json_msg.encode(encoding='utf-8')


def message_to_json(msg: bytes):
    return json.loads(msg)
