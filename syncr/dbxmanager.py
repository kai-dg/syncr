#!/usr/bin/env python3
import os
import json
import dropbox
import zipfile
import shutil
from distutils.dir_util import copy_tree
from uuid import uuid4
from . import settings as s
from . import database as db
OVERWRITE = dropbox.files.WriteMode.overwrite


def unzipper(data, dest, dbxfolder):
    zipf = os.path.join(dest, "temp.zip")
    with open(zipf, "wb+") as f:
        f.write(data)
    with zipfile.ZipFile(zipf, 'r') as z:
        # Create temp folder to hold files & delete after
        temp = os.path.join(dest, str(uuid4()))
        os.mkdir(temp)
        z.extractall(temp)
        # Extracting adds extra folder named the dbx's last folder name
        src = os.path.join(temp, dbxfolder.split("/")[-1])
        copy_tree(src, dest)
    # Remove temp folder and zip file
    shutil.rmtree(temp)
    os.remove(zipf)
    return True

class DbxManager:
    def __init__(self):
        self.dbx = None

    def init_dbx(self, token):
        try:
            return dropbox.Dropbox(token) if token else quit()
        except Exception as e:
            print(f"{s.PREFIX} Error => {str(e)}")
            quit()

    def check_args(self, args):
        if not 0 < len(args) < 3:
            print(f"{s.PREFIX} Need account name and folder name.")
            quit()
        folder = "/" if len(args) == 1 else args[1]
        folder = "/" + args[1] if folder[0] != "/" else folder
        acc = args[0]
        self.dbx = self.init_dbx(db.read_token(acc))
        return (folder, acc)

    def status(self, args):
        folder, acc = self.check_args(args)
        check = self.check_for_folder(folder)
        if not check:
            quit()
        print(f"{s.PREFIX} Account: {s.BLUE}{acc}{s.END}")
        print(f"{s.PREFIX} Listing all folders in {s.GREEN}{folder}{s.END}:")
        for entry in self.dbx.files_list_folder(folder).entries:
            if entry.__class__.__name__ == "FolderMetadata":
                print(f"  > {s.BLUE}{entry.name}{s.END}")

    def create(self, args):
        folder, acc = self.check_args(args)
        if args == []:
            return print("{s.PREFIX} Need a folder name to create in dropbox")
        try:
            meta = self.dbx.files_create_folder(folder)
            print(f"{s.PREFIX} Created {s.GREEN}{folder}" +
                  f"{s.END} in dropbox")
        except Exception as e:
            if "WriteConflictError" in str(e):
                return print(f"{s.PREFIX} {s.GREEN}{folder}" +
                             f"{s.END} already exists in dropbox")
            return print(f"{s.PREFIX} ERROR => {str(e)}")

    def delete(self, args):
        folder, acc = self.check_args(args)
        if args == []:
            return print("{s.PREFIX} Need a folder name to delete in dropbox")
        try:
            confirm = input(f"{s.PREFIX} Are you sure you want to delete" +
                            f" {s.GREEN}{folder}{s.END} " +
                            "from dropbox? (y/n)\n")
            if confirm == "y":
                meta = self.dbx.files_delete(folder)
                print(f"{s.PREFIX} Deleted {s.GREEN}{folder}" +
                      f"{s.END} in dropbox")
            else:
                return print(f"{s.PREFIX} Canceled deletion of {s.GREEN}" +
                             f"{folder}{s.END}")
        except Exception as e:
            if "LookupError" in str(e):
                return print(f"{s.PREFIX} {s.GREEN}{folder}{s.END} does " +
                             "not exist in dropbox")
            return print(f"{s.PREFIX} ERROR => {str(e)}")

    def upload(self, folder, f):
        try:
            with open(f, "rb") as b:
                dbxpath = folder + "/" + f if f[0] != "/" else folder + f
                self.dbx.files_upload(b.read(), dbxpath, OVERWRITE, mute=True)
                print(f"{s.PREFIX} Uploaded {s.GREEN}{f}" +
                      f"{s.END} to Dropbox => {folder}")
        except Exception as e:
            return print(f"{s.PREFIX} ERROR => {str(e)}")

    def download(self, folder, dest):
        try:
            check = self.dbx.files_download_zip(folder)
        except Exception as e:
            if "LookupError" in str(e):
                return print(f"{s.PREFIX} Could not find {s.GREEN}{folder}" +
                             f"{s.END} in dropbox")
            else:
                return print(f"{s.PREFIX} ERROR => {str(e)}")
        zipbytes = check[-1].content
        zipping = unzipper(zipbytes, dest, folder)
        return print(f"{s.PREFIX} Updated this folder from dropbox {folder}")

    def check_for_folder(self, folder):
        check = False
        try:
            for entry in self.dbx.files_list_folder("", recursive=True).entries:
                if entry.__class__.__name__ == "FolderMetadata":
                    if folder == entry.path_lower:
                        check = True
            if not check:
                print(f"{s.PREFIX} Folder {s.GREEN}{folder}{s.END} could not" +
                      " be found in dropbox")
                print(f"{s.PREFIX} Create it with the dbxcreate")
        except Exception as e:
            print(f"{s.PREFIX} ERROR => {str(e)}")
        return check

