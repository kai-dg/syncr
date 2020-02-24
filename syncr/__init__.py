#!/usr/bin/env python3
import os
import copy
import glob
from cryptography.fernet import Fernet
from os.path import getmtime
from .dbxmanager import DbxManager
from . import settings as s
from . import database as db


def read_token(dbxacc):
    if not dbxacc:
        return None
    try:
        with open(s.TOKENPATH, "r") as f:
            tokenstr = [l.strip() for l in f.readlines()]
            for t in tokenstr:
                t = t.split()
                tokens = (t[1], t[2]) if t[0] == dbxacc else None
            if not tokens:
                return print(f"{s.PREFIX} {dbxacc} doesn't have a token, " +
                             "use dbxaddtoken")
            try:
                f = Fernet(str.encode(tokens[0]))
                return f.decrypt(str.encode(tokens[1])).decode()
            except Exception as e:
                print(f"{s.PREFIX} Credentials Error => {e.__class__}")
                return print(e)
    except FileNotFoundError:
        return add_token()

def add_token():
    token = input(f"{s.PREFIX} What is your token?\n")
    name = input(f"{s.PREFIX} Give a 1 word name for this dropbox account\n")
    if len(name.split()) != 1:
        print(f"{s.PREFIX} Are you incapable of reading instructions?")
        quit()
    key = Fernet.generate_key()
    f = Fernet(key)
    enc = f.encrypt(str.encode(token.strip())).decode()
    with open(s.TOKENPATH, "w") as f:
        data = name + " " + key.decode().strip() + " " + enc
        f.write(data)
        print(f"{s.PREFIX} Token for {name} has been saved")
        return token.strip()

class Syncr(DbxManager):
    def __init__(self, args):
        self.dm = DbxManager
        self.addmessage = []
        self.dbxpath = db.read(s.DBXPATH) if db.read(s.DBXPATH) != {} else self.init(args[1:])
        self.dbxacc = self.dbxpath.get("dbxacc", None)
        self.syncadd = db.read(s.ADDPATH)
        self.compare = copy.deepcopy(self.syncadd)
        self.commands = {
            "dbxlist": self.dm(read_token(self.dbxacc)).status,
            "init": self.init,
            "add": self.add,
            "rm": self.remove,
            "dbxcreate": self.dm(read_token(self.dbxacc)).create,
            "dbxdelete": self.dm(read_token(self.dbxacc)).delete
        }
        self.single_commands = {
            "dbxlist": self.dm(read_token(self.dbxacc)).status,
            "push": self.push,
            "pull": self.pull,
            "status": self.status
        }
        self.run_args(args)

    def run_args(self, args):
        if len(args) == 0:
            return print(f"{s.PREFIX} reading the readme can save you A LOT of time")
        if args[0] not in list(self.commands) and args[0] \
                   not in list(self.single_commands):
            return print(f"{s.PREFIX} {args[0]} is not a command")
        if len(args) < 2:
            self.single_commands[args[0]]()
        else:
            try:
                self.commands[args[0]](args[1:])
            except Exception as e:
                print(f"{s.PREFIX} ERROR => {str(e)}")
                return print(f"{s.PREFIX} {args[0]} needs an argument")

    def init(self, args):
        if len(args) != 2:
            print(f"{s.PREFIX} Need to init an account name and " +
                  "folder name from your dropbox")
            return {}

        folder = ("/" + args[1]) if args[1][0] != "/" else args[1]
        name = args[0]
        if not os.path.exists(s.DBXPATH):
            if not os.path.exists(s.DATAFOLDER):
                os.mkdir(s.DATAFOLDER)
            self.dbxacc = name
            syncadd = {"folder": folder, "dbxacc": name}
            db.write(s.DBXPATH, syncadd, writemode="w")
            db.write(s.ADDPATH, {}, writemode="w")
            print(f"{s.PREFIX} initialized dropbox folder {s.GREEN}{folder}" +
                  f"{s.END} in dropbox account {s.BLUE}{name}{s.END}")
        else:
            print(f"{s.PREFIX} this folder already has an init")

        self.dm = self.dm(read_token(self.dbxacc))
        folder_exists = self.dm.check_for_folder(folder)
        if not folder_exists:
            print(f"{s.PREFIX} Folder {s.GREEN}{folder}{s.END} could not" +
                  " be found dropbox")
            return print(f"{s.PREFIX} Create it with the dbxcreate command")
        quit()

    def push(self):
        print(f"{s.PREFIX} Reminder, currently can only push files under" +
              f" {s.RED}5MB{s.END}")
        self.dm = self.dm(read_token(self.dbxacc))
        folder = self.dbxpath["folder"]
        pushed = False
        for f in self.syncadd:
            if self.syncadd[f]["pushed"] == False:
                self.dm.upload(folder, f)
                self.syncadd[f]["pushed"] = True
                pushed = True
        db.write(s.ADDPATH, self.syncadd)
        if pushed:
            return print(f"{s.PREFIX} Finished pushing")
        else:
            return print(f"{s.PREFIX} Nothing is queued to push")

    def ignorer(self):
        # TODO Add regex for strict membership test
        ignore = db.read(s.IGNOREPATH, "text").split()
        res = {}
        addkeys = list(self.compare)
        for i in ignore:
            f = i[1:] if i[0] == os.sep else i
            f = f[:-1] if f[-1] == os.sep else f
            f = f.split(os.sep)
            check = [s for s in addkeys if f[0] in s]
            if len(f) == 1:
                check = f
            if check != []:
                for c in check:
                    self.compare.pop(c, None)
                    self.addmessage.remove(f"{s.PREFIX} {s.GREEN}{c}{s.END} " +
                    "is queued to push")

    def add_single(self, f):
        fpath = os.path.join(s.CWDPATH, f)
        f = f[:-1] if f[-1] == os.sep else f
        if not os.path.exists(fpath):
            return False
        mod = getmtime(fpath)
        size = os.path.getsize(fpath)
        self.compare[f] = {} if not self.compare.get(f, None) \
                          else self.compare[f]
        if self.compare[f].get("size", None) != size:
            self.compare[f]["mod"] = mod
            self.compare[f]["pushed"] = False
            self.addmessage.append(f"{s.PREFIX} {s.GREEN}{f}{s.END} " +
                                   "is queued to push")
        self.compare[f]["size"] = size
    
    def add_all(self):
        for root, dirs, files in os.walk(s.CWDPATH, topdown=False):
            for f in files:
                path = os.path.join(s.CWDPATH, root, f)
                if "syncr" not in path:
                    subdirs = root.replace(s.CWDPATH, "")
                    if subdirs != "":
                        subdirs = subdirs[1:] if subdirs[0] == "/" else subdirs
                        self.add_single(os.path.join(subdirs, f))
                    else:
                        self.add_single(f)

    def add(self, files):
        """files (list): List of args"""
        if self.dbxpath == {}:
            return print(f"{s.PREFIX} Run syncr init to initialize this folder")
        if files[0] == ".":
            self.add_all()
        else:
            for f in files:
                self.add_single(f)
        self.ignorer()
        if self.compare != self.syncadd:
            db.write(s.ADDPATH, self.compare)
            message = "\n".join(self.addmessage)
            print(f"{message}")
        else:
            print(f"{s.PREFIX} No changes detected at all")

    def pull(self):
        self.dm = self.dm(read_token(self.dbxacc))
        folder = self.dbxpath["folder"]
        self.dm.download(folder, s.CWDPATH)

    def remove(self, files):
        pass

    def status(self):
        print(f"{s.PREFIX} STATUS {s.GREEN}{s.CWDPATH}{s.END}:")
        notpushed = []
        for f in self.syncadd:
            if not self.syncadd[f]["pushed"]:
                notpushed.append(f)
        if len(notpushed) > 0:
            print(f"  > Not pushed:")
        else:
            print(f"  > Everything is up to date.")
        for p in notpushed:
            print(f"\t{s.RED}{p}{s.END}")
