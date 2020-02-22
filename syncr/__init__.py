#!/usr/bin/env python3
import os
import copy
import glob
from cryptography.fernet import Fernet
from os.path import getmtime
from .dbxmanager import DbxManager
from . import settings as s
from . import database as db


def read_token():
    try:
        with open(s.TOKENPATH, "r") as f:
            tokens = f.read().split()
            try:
                f = Fernet(str.encode(tokens[0]))
                return f.decrypt(str.encode(tokens[1])).decode()
            except Exception as e:
                print(f"{s.PREFIX} Credentials Error => {e.__class__}")
                return print(e)
    except FileNotFoundError:
        token = input("{s.PREFIX} What is your token?\n")
        key = Fernet.generate_key()
        f = Fernet(key)
        enc = f.encrypt(str.encode(token.strip())).decode()
        with open(s.TOKENPATH, "w") as f:
            data = key.decode().strip() + " " + enc
            f.write(data)
            print("{s.PREFIX} Token has been saved")
        return token.strip()

class Syncr(DbxManager):
    def __init__(self, args):
        self.dbxpath = db.read(s.DBXPATH)
        self.syncadd = db.read(s.ADDPATH)
        self.compare = copy.deepcopy(self.syncadd)
        self.ignore = db.read(s.IGNOREPATH, "text").split()
        self.dm = DbxManager
        self.commands = {
            "init": self.init,
            "add": self.add,
            "rm": self.remove,
            "dbxcreate": self.dm(read_token()).create,
            "dbxdelete": self.dm(read_token()).delete
        }
        self.single_commands = {
            "ignore": self.ignorer,
            "push": self.push,
            "pull": self.pull,
            "status": self.status
        }
        self.run_args(args)

    def run_args(self, args):
        if len(args) == 0:
            return print("{s.PREFIX} give me a command")
        if args[0] not in list(self.commands) and args[0] \
                   not in list(self.single_commands):
            return print(f"{s.PREFIX} {args[0]} is not a command")
        try:
            self.single_commands[args[0]]()
        except Exception as e:
            if len(args) < 2:
                print(f"> Syncr: ERROR => {str(e)}")
                return print(f"Syncr: {args[0]} needs an argument")
            self.commands[args[0]](args[1:])

    def ignorer(self):
        # Glob for files
        # Check if directory for /* or */
        for i in self.ignore:
            print(i)
            f = i[1:] if i[0] == os.sep else i
            ignore = os.path.join(s.CWDPATH, f)

    def init(self, args):
        self.dm = self.dm(read_token())
        if len(args) < 1:
            return print(f"{s.PREFIX} Need to init a folder name from your dropbox")
        folder = ("/" + args[0]) if args[0][0] != "/" else args[0]
        folder_exists = self.dm.check_for_folder(folder)
        if not folder_exists:
            print(f"{s.PREFIX} Folder {folder} could not be found dropbox")
            return print("> Syncr: Create it with the dbxcreate command")
        if not os.path.exists(s.DBXPATH):
            if not os.path.exists(s.DATAFOLDER):
                os.mkdir(s.DATAFOLDER)
            syncadd = {"folder": folder}
            db.write(s.DBXPATH, syncadd, writemode="w")
            db.write(s.ADDPATH, {}, writemode="w")
            print(f"{s.PREFIX} initialized dropbox folder {folder}")
        else:
            print(f"{s.PREFIX} this folder already has an init")

    def push(self):
        print("{s.PREFIX} Reminder, currently can only push files under 5MB")
        self.dm = self.dm(read_token())
        folder = self.dbxpath["folder"]
        pushed = False
        for f in self.syncadd:
            if self.syncadd[f]["pushed"] == False:
                self.dm.upload(folder, f)
                self.syncadd[f]["pushed"] = True
                pushed = True
        db.write(s.ADDPATH, self.syncadd)
        if pushed:
            return print("{s.PREFIX} Finished pushing")
        else:
            return print("{s.PREFIX} Nothing is queued to push")

    def add_single(self, f):
        fpath = os.path.join(s.CWDPATH, f)
        if os.path.exists(fpath):
            self.compare[f] = {} if not self.compare.get(f, None) \
                              else self.compare[f]
            mod = getmtime(fpath)
            size = os.path.getsize(fpath)
            # Need better modification detection
            if self.compare[f].get("size", None) != size:
                self.compare[f]["mod"] = mod
                self.compare[f]["pushed"] = False
                print(f"{s.PREFIX} {f} is queued to push")
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
            return print("{s.PREFIX} Run syncr init to initialize this folder")
        if files[0] == ".":
            self.add_all()
        else:
            for f in files:
                self.add_single(f)
        if self.compare != self.syncadd:
            db.write(s.ADDPATH, self.compare)
        else:
            print("{s.PREFIX} No changes detected at all")

    def pull(self):
        self.dm = self.dm(read_token())
        folder = self.dbxpath["folder"]
        self.dm.download(folder, s.CWDPATH)

    def remove(self, files):
        pass

    def status(self):
        print(f"{s.PREFIX} STATUS {s.Colors.GREEN}{s.CWDPATH}{s.Colors.END}:")
        notpushed = []
        for f in self.syncadd:
            if not self.syncadd[f]["pushed"]:
                notpushed.append(f)
        print(f"  > Not pushed:")
        for p in notpushed:
            print(f"\t{s.Colors.RED}{p}{s.Colors.END}")
