#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
SYNOPSIS
    python build_db.py [options]
OPTIONS
    help <command>
        show this help, or help to command
    initenv <dir>
        initialize a customized environment
    runserver <options>
        run portal service, note you should execute this command under your
        customized environment, else you can't read your config file
    runblt
        run BLT service, note you should execute this command under your
        customized environment, else you can't read your config file
"""
import sys
import subprocess
import os
import shutil

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "help":
        try:
            command = sys.argv[2]
            if command == "initenv":
                print "initenv <dir>"
                print "initialize a customized environment"
            elif command == "runserver":
                subprocess.call(["python", "-m", "lite_mms.runserver", "-h"]) 
            elif command == "runblt":
                subprocess.call(["python", "-m", "lite_mms.BLT", "-h"])
        except IndexError:
            print __doc__
        finally:
            exit(0)
    elif sys.argv[1] == "runserver":
        subprocess.call(["python", "-m", "lite_mms.runserver"] + sys.argv[2:])
    elif sys.argv[1] == "runblt":
        subprocess.call(["python", "-m", "lite_mms.BLT"] + sys.argv[2:])
    elif sys.argv[1] == "initenv":
        if len(sys.argv) != 3:
            print __doc__
            exit(-1)
        if os.path.exists(sys.argv[2]):
            print "Error: " + sys.argv[2] + " exists"
            exit(-1)
        os.makedirs(sys.argv[2])
        os.chdir(sys.argv[2])
        config_fpath = os.path.join(sys.prefix, "share/lite-mms/config.py.sample")
        if not os.path.exists(config_fpath):
            print "Error: " + config_fpath + "doesn't exists, make sure your installation completed"
        shutil.copy(config_fpath, "config.py")
        readme_fpath = os.path.join(sys.prefix, "share/lite-mms/readme.txt")
        if not os.path.exists(readme_fpath):
            print "Error: " + readme_fpath + "doesn't exists, make sure your installation completed"
            exit(-1)
        shutil.copy(readme_fpath, "readme.txt")
        tools_dir = os.path.join(sys.prefix, "share/lite-mms/tools")
        if not os.path.exists(tools_dir):
            print "Error: " + tools_dir + "doesn't exists, make sure your installation completed"
            exit(-1)
        shutil.copytree(tools_dir, "tools")
        subprocess.call(["chmod", "u+x", "tools/add_uwsgi_app.sh"])
    else:
        print "unkown option: " + sys.argv[1]
        print __doc__
