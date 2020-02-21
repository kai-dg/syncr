#!/usr/bin/env python3
import os
import json
import dropbox
import zipfile
import shutil
OVERWRITE = dropbox.files.WriteMode.overwrite


def unzipper(data, dest):
    zipf = os.path.join(dest, "temp.zip")
    with open(zipf, "wb+") as f:
        f.write(data)
    with zipfile.ZipFile(zipf, 'r') as z:
        files = [f.filename for f in z.filelist]
        # Safe extract with dest
        for f in files[1:]:
            z.extract(f, dest)
        src = os.path.join(dest, files[0].replace("/", ""))
        files = os.listdir(src)
        for f in files:
            shutil.move(os.path.join(src, f), dest)
    os.rmdir(src)
    os.remove(zipf)
    return True

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
        zipping = unzipper(zipbytes, dest)
        print(f"> Syncr: Downloaded all from dropbox {folder}")
