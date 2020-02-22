#!/usr/bin/env python3
import os
CWDPATH = os.getcwd()
ABSPATH = os.path.dirname(os.path.realpath(__file__))
DATAFOLDER = os.path.join(CWDPATH, ".syncr")
ADDPATH = os.path.join(DATAFOLDER, ".syncradd.json")
DBXPATH = os.path.join(DATAFOLDER, ".dbxpath.json")
TOKENPATH = os.path.join(ABSPATH, ".synctoken")
IGNOREPATH = os.path.join(CWDPATH, ".syncrignore")
