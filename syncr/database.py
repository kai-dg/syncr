#!/usr/bin/env python3
import json
from . import settings as s
from cryptography.fernet import Fernet


def read(filepath, mode=None):
    try:
        with open(filepath, "r") as f:
            data = f.read().strip() if mode == "text" else json.load(f)
    except:
        data = "" if mode == "text" else {}
    return data

def write(filepath, data, mode=None, writemode="w+"):
    """Default mode writes to JSON, other mode is 'text'"""
    try:
        with open(filepath, writemode) as f:
            if mode == "text":
                f.write(data)
            else:
                json.dump(data, f)
            return True
    except:
        return False

def add_token():
    token = input(f"{s.PREFIX} What is your token?\n")
    name = input(f"{s.PREFIX} Give a 1 word name for this dropbox account\n")
    if len(name.split()) != 1:
        print(f"{s.PREFIX} Are you incapable of reading instructions?")
        quit()
    key = Fernet.generate_key()
    f = Fernet(key)
    enc = f.encrypt(str.encode(token.strip())).decode()
    data = read(s.TOKENPATH)
    data[name] = (key.decode().strip() + " " + enc)
    write(s.TOKENPATH, data)
    print(f"{s.PREFIX} Token for {name} has been saved")
    return quit()

def read_token(dbxacc):
    if not dbxacc:
        return None
    data = read(s.TOKENPATH)
    keys = data.get(dbxacc, None)
    if not keys:
        print(f"{s.PREFIX} Acc {dbxacc} does not exist. Try adding it?")
        add_token()
    keys = keys.split()
    f = Fernet(str.encode(keys[0]))
    return f.decrypt(str.encode(keys[1])).decode()
