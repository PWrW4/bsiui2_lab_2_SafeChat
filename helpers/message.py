import json


def create_message(action: str, arg1=None, arg2=None, arg3=None):
    if action == "M" or action == "ERROR":
        msg = {"action": action, "message": str(arg1)}
    elif action == "L" or action == "R":
        msg = {"action": action, "login": str(arg1), "password": str(arg2), "port": int(arg3)}
    elif action == "UU":
        msg = {"action": action, "ulist": arg1}
    elif action == "CT":
        msg = {"action": action, "nick": str(arg1), "token": str(arg2)}
    elif action == "OK" or action == "HELLO" or action == "OUT":
        msg = {"action": action}
    else:
        return "ERROR - action not found"
    json_msg = json.dumps(msg)
    return json_msg.encode(encoding='utf-8')


def message_to_json(msg: bytes):
    return json.loads(msg)
