# Syncr

Dropbox API Wrapper terminal tool. Helps sync your code if you work on 2 or more computers, works like `git`.

---
## Commands

* `syncr dbxcreate DROPBOX_FOLDER_NAME`
  - Creates a folder in your dropbox's root directory
* `syncr dbxdelete DROPBOX_FOLDER_NAME`
  - Deletes a folder in your dropbox's root directory
* `syncr init DROPBOX_FOLDER_NAME`
  - Inits the current folder with the folder in your dropbox
* `syncr add FILENAME*`
  - Adds file(s) to the queue to push
* `syncr push`
  - Pushes the added files to dropbox
* `syncr pull`
  - Downloads all files from the set dropbox folder

---
## Author
**Derrick Gee** - [kai-dg](https://github.com/kai-dg)
