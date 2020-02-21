#!/usr/bin/env python3
import os
from cryptography.fernet import Fernet
from os.path import getmtime
from .dbxmanager import DbxManager
from . import settings as s
from . import database as db


def read_token():
    if os.path.exists(s.TOKENPATH):
        with open(s.TOKENPATH, "r") as f:
            tokens = f.read().split()
            try:
                f = Fernet(str.encode(tokens[0]))
                return f.decrypt(str.encode(tokens[1])).decode()
            except Exception as e:
                print(f"> Syncr: Credentials Error => {e.__class__}")
                return print(e)
    else:
        token = input("> Syncer: What is your token?\n")
        key = Fernet.generate_key()
        f = Fernet(key)
        enc = f.encrypt(str.encode(token.strip())).decode()
        with open(s.TOKENPATH, "w") as f:
            data = key.decode().strip() + " " + enc
            f.write(data)
            print("> Syncr: Token has been saved")
        return token.strip()

class Syncr(DbxManager):
    def __init__(self, args):
        self.dm = DbxManager
        self.commands = {
            "test": self.test,
            "init": self.init,
            "add": self.add,
            "rm": self.remove,
            "dbxcreate": self.dm(read_token()).create,
            "dbxdelete": self.dm(read_token()).delete
        }
        self.single_commands = {
            "push": self.push,
            "pull": self.pull,
            "status": self.status
        }
        self.dbxpath = db.read(s.DBXPATH)
        self.syncadd = db.read(s.ADDPATH)
        self.run_args(args)

    def run_args(self, args):
        if len(args) == 0:
            return print("> Syncr: give me a command")
        if args[0] not in list(self.commands) and args[0] \
                   not in list(self.single_commands):
            return print(f"> Syncr: {args[0]} is not a command")
        try:
            self.single_commands[args[0]]()
        except:
            if len(args) < 2:
                return print(f"Syncr: {args[0]} needs an argument")
            self.commands[args[0]](args[1:])

    def test(self, args):
        self.dm = self.dm(read_token())
        print(self.dm.check_for_folder(args[0]))

    def init(self, args):
        self.dm = self.dm(read_token())
        if len(args) < 1:
            return print(f"> Syncr: Need to init a folder name from your dropbox")
        folder = ("/" + args[0]) if args[0][0] != "/" else args[0]
        folder_exists = self.dm.check_for_folder(folder)
        if not folder_exists:
            print(f"> Syncr: Folder {folder} could not be found dropbox")
            return print("> Syncr: Create it with the dbxcreate command")
        if not os.path.exists(s.DBXPATH):
            if not os.path.exists(s.DATAFOLDER):
                os.mkdir(s.DATAFOLDER)
            syncadd = {"folder": folder}
            db.write(s.DBXPATH, syncadd, writemode="w")
            db.write(s.ADDPATH, {}, writemode="w")
            print(f"> Syncr: initialized dropbox folder {folder}")
        else:
            print(f"> Syncr: this folder already has an init")


    def push(self):
        print("> Syncr: Reminder, currently can only push files under 5MB")
        self.dm = self.dm(read_token())
        folder = self.dbxpath["folder"]
        pushed = False
        for f in self.syncadd:
            if self.syncadd[f]["pushed"] == False:
                self.dm.upload(folder, f, self.syncadd[f]["path"])
                self.syncadd[f]["pushed"] = True
                pushed = True
        db.write(s.ADDPATH, self.syncadd)
        if pushed:
            return print("> Syncr: Finished pushing")
        else:
            return print("> Syncr: Nothing is queued to push")

    def add_all(self):
        for root, dirs, files in os.walk(s.CWDPATH):
            for f in files:
                root = root[1:] if root[0] == "." else root
                root = root[1:] if root[0] == "/" else root
                path = os.path.join(s.CWDPATH, root, f)
                print(path)

    def add(self, files):
        """files (list): List of args"""
        data = self.syncadd.copy()
        if self.dbxpath == {}:
            return print("> Syncr: Run syncr init to initialize this folder")
        for f in files:
            fpath = os.path.join(s.CWDPATH, f)
            if os.path.exists(fpath):
                data[f] = {} if not data.get(f, None) else data[f]
                mod = getmtime(fpath)
                size = os.path.getsize(fpath)
                data[f]["path"] = f
                # Need better modification detection
                if data[f].get("size", None) != size:
                    data[f]["mod"] = mod
                    data[f]["pushed"] = False
                    print(f"> Syncr: {f} is queued to push")
                data[f]["size"] = size
        if data != self.syncadd:
            db.write(s.ADDPATH, data)
        else:
            print("> Syncr: No changes detected at all")

    def pull(self):
        self.dm = self.dm(read_token())
        folder = self.dbxpath["folder"]
        self.dm.download(folder, s.CWDPATH)
        return print(f"> Syncr: Updated this folder from dropbox {folder}")

    def remove(self, files):
        pass

    def status(self):
        pass
