#!/usr/bin/env python3
import dropbox
import os
import json
from os.path import getmtime
CWDPATH = os.getcwd()
ABSPATH = os.path.dirname(os.path.realpath(__file__))
DATAFOLDER = os.path.join(ABSPATH, ".syncdata")
ADD_DATA = os.path.join(DATAFOLDER, ".syncadd.json")
"""
try:
    with open(ADD_DATA, "r") as f:
        SYNCADD = json.load(f)
except FileNotFoundError:
    os.mkdir(DATAFOLDER) if not os.path.exists(DATAFOLDER)
    with open(ADD_DATA, "w") as f:
        f.write("{}")
        SYNCADD = {}
"""

def detect_change(f, mod, size):
    if SYNCADD[f]["mod"] != mod or SYNCADD[f]["size"] != size:
        print(f"> Syncr: added {f}")
        return {"mod": mod, "size": size}
    print(f"> No changes detected for {f}")
    return None

class Syncr:
    def __init__(self):
        self.dbx = dropbox.Dropbox("")

    def init(self):
        if not os.path.exists(ADD_DATA):
            if not os.path.exists(DATAFOLDER):
                os.mkdir(DATAFOLDER)
            with open(ADD_DATA, "w") as f:
                f.write("{}")
                SYNCADD = {}
        else:
            print(f"> Syncr: this folder already has init")

    def write(self, data):
        with open(ADD_DATA, "w+") as f:
            json.dump(data, f)

    def add(self, files):
        """files (list): List of args"""
        data = SYNCADD
        for f in files:
            fpath = os.path.join(CWDPATH, f)
            if os.path.exists(fpath):
                mod = getmtime(fpath)
                size = os.path.getsize(fpath)
                if data.get(f, None):
                    check = detect_change(f, mod, size)
                    if not check:
                        pass
                    else:
                        data[f] = check
                else:
                    data[f] = {"mod": mod, "size": size}
        if data != SYNCADD:
            write(data)
        else:
            print("> No changes detected at all")

    def remove(self, files):
        pass

    def status(self):
        pass

    def pull(self):
        for entry in self.dbx.files_list_folder('/development').entries:
            print(entry.name)
