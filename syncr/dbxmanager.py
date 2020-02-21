#!/usr/bin/env python3
import json
import dropbox
OVERWRITE = dropbox.files.WriteMode.overwrite


class DbxManager:
    def __init__(self, token):
        self.dbx = dropbox.Dropbox(token)

    def check_folder(self, folder):
        try:
            for entry in self.dbx.files_list_folder(folder).entries:
                print(entry.name)
        except Exception as e:
            if "ListFolderError" in str(e):
                return print("> Syncr: Folder name could not be found dropbox")
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
            meta = self.dbx.files_delete(folder)
            print(f"> Syncr: Deleted {folder} in dropbox")
        except Exception as e:
            if "LookupError" in str(e):
                return print(f"> Syncr: {folder} does not exist in dropbox")
            return print(f"> Syncr: ERROR => {str(e)}")

    def upload(self, folder, f):
        try:
            with open(f, "rb") as b:
                filename = f.split("/")[-1]
                folder += "/" + filename
                self.dbx.files_upload(b.read(), folder, OVERWRITE, mute=True)
                print(f"> Syncr: Uploaded {f} to Dropbox => {folder}")
        except Exception as e:
            return print(f"> Syncr: ERROR => {str(e)}")
