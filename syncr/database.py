#!/usr/bin/env python3
import json


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
