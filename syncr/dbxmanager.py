#!/usr/bin/env python3
import os
import json
import dropbox
import zipfile
from pathlib import Path
OVERWRITE = dropbox.files.WriteMode.overwrite


class DbxManager:
    def __init__(self, token):
        self.dbx = dropbox.Dropbox(token)

    def check_for_folder(self, folder):
        try:
            for entry in self.dbx.files_list_folder("").entries:
                if "Folder" in str(entry.__class__):
                    if folder.replace("/", "") == entry.name:
                        return True
            return False
        except Exception as e:
            return print(f"> Syncr: ERROR => {str(e)}")

    def create(self, args):
        if args == []:
            return print("> Syncr: Need a folder name to create in dropbox")
        folder = ("/" + args[0]) if args[0][0] != "/" else args[0]
        try:
            meta = self.dbx.files_create_folder(folder)
            print(f"> Syncr: Created {folder} in dropbox")
        except Exception as e:
            if "WriteConflictError" in str(e):
                return print(f"> Syncr: {folder} already exists in dropbox")
            return print(f"> Syncr: ERROR => {str(e)}")

    def delete(self, args):
        if args == []:
            return print("> Syncr: Need a folder name to delete in dropbox")
        folder = ("/" + args[0]) if args[0][0] != "/" else args[0]
        try:
            confirm = input(f"Are you sure you want to delete {folder}" +
                             "from dropbox?")
            if confirm == "y":
                meta = self.dbx.files_delete(folder)
                print(f"> Syncr: Deleted {folder} in dropbox")
            else:
                return print(f"> Syncr: Canceled deletion of {folder}")
        except Exception as e:
            if "LookupError" in str(e):
                return print(f"> Syncr: {folder} does not exist in dropbox")
            return print(f"> Syncr: ERROR => {str(e)}")

    def upload(self, folder, f, path):
        try:
            with open(f, "rb") as b:
                dbxpath = folder + "/" + path if path[0] != "/" else folder + path
                self.dbx.files_upload(b.read(), dbxpath, OVERWRITE, mute=True)
                print(f"> Syncr: Uploaded {f} to Dropbox => {folder}")
        except Exception as e:
            return print(f"> Syncr: ERROR => {str(e)}")

    def download(self, folder, dest):
        check = self.dbx.files_download_zip(folder)
        zipbytes = check[-1].content
        folder = os.path.join(dest, "temp.zip")
        with open(folder, "wb") as f:
            f.write(zipbytes)
        with zipfile.ZipFile(folder, 'r') as zip_ref:
            p = Path(dest)
            zip_ref.extractall(p.parent)
        os.remove(folder)
