#!/usr/bin/env python3
import os
import json
import dropbox
import zipfile
import shutil
from . import settings as s
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

    def status(self, folder=""):
        if folder != "":
            folder = "/" + folder[0] if folder[0][0] != "/" else folder[0]
        print(f"{s.PREFIX} Listing all folders in {s.GREEN}{folder}{s.END}:")
        for entry in self.dbx.files_list_folder(folder).entries:
            if entry.__class__.__name__ == "FolderMetadata":
                print(f"  > {s.BLUE}{entry.name}{s.END}")

    def check_for_folder(self, folder):
        try:
            for entry in self.dbx.files_list_folder("", recursive=True).entries:
                if entry.__class__.__name__ == "FolderMetadata":
                    if folder == entry.path_lower:
                        return True
            return False
        except Exception as e:
            return print(f"{s.PREFIX} ERROR => {str(e)}")

    def create(self, args):
        if args == []:
            return print("{s.PREFIX} Need a folder name to create in dropbox")
        folder = ("/" + args[0]) if args[0][0] != "/" else args[0]
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
        if args == []:
            return print("{s.PREFIX} Need a folder name to delete in dropbox")
        folder = ("/" + args[0]) if args[0][0] != "/" else args[0]
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
        zipping = unzipper(zipbytes, dest)
        return print(f"{s.PREFIX} Updated this folder from dropbox {folder}")
