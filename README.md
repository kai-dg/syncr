# Syncr

Dropbox SDK Wrapper terminal tool. If you work on 2 or more computers, helps sync config folders or local projects through your dropbox account. Works like `git` a little.

---
## Getting your Dropbox Access Token

1. Sign into the App Console: [https://www.dropbox.com/developers/apps?_tk=pilot_lp&_ad=topbar4&_camp=myapps](https://www.dropbox.com/developers/apps?_tk=pilot_lp&_ad=topbar4&_camp=myapps)

2. Create App
    * Check Dropbox API
    * Check Full Dropbox Access
    * Name your app whatever

3. Under OAuth 2, Generate access token

4. Insert access token when asked
```
$ syncr init NAME /test
> Syncr: What is your token?
PASTE TOKEN FROM STEP 3 HERE AND ENTER
```

---
## Commands

* `syncr dbxcreate ACC_NAME DROPBOX_FOLDER_NAME`
  - Creates a folder in your dropbox's root directory
* `syncr dbxdelete ACC_NAME DROPBOX_FOLDER_NAME`
  - Deletes a folder in your dropbox's root directory
* `syncr dbxlist ACC_NAME *FOLDER_NAME`
  - Lists all folders in your dropbox
* `syncr dbxaddtoken`
  - Adds a dropbox account token with a name associated to it
* `syncr init ACC_NAME DROPBOX_FOLDER_NAME`
  - Inits the current folder with the folder in your dropbox
* `syncr add FILEPATH`
  - Adds file(s) to the queue to push, use `.` for all in current path
* `syncr push`
  - Pushes the added files to dropbox
* `syncr pull`
  - Downloads all files from the set dropbox folder
* `syncr status`
  - Shows what is not pushed yet in a folder with init

- `*` means optional

---
## Syncrignore

You can add `.syncrignore` into the root of a directory with the init in it, to ignore all files with matching names to it.

**Wildcard not supported yet**

*Example*
```
> ~/test$ ls
hello.txt foo.py
> ~/test$ cat .syncrignore
foo.py
> ~/test$ syncr add .
> Syncr: hello.txt is queued to push
> ~/test$
```

---
## Author
**Derrick Gee** - [kai-dg](https://github.com/kai-dg)
