#! /usr/bin/env python
# -*- coding: UTF-8 -*-
"""
A WEB HOOK for github
SYNOPSIS
    python deploy_web_hook.py [options]
OPTIONS
    -h 
        show this help
    -p  <port>
        the port of server runs on
    -s  <host>
        the ip of the server runs on
    -f  <fabfile>
        the fabfile to execute
"""
import sys
from getopt import getopt
from flask import Flask, request

opts, _ = getopt(sys.args[1:], "f:s:p:h")

host = None
port = None
for o, v in opts:
    if o == "-s":
        host = v
    elif o == "-p":
        port = int(v)
    elif o == "-h":
        print __doc__
    elif o == "-f":
        fabfile = v
    else:
        print "unkown option: " + o
        print __doc__
        sys.exit(-1)

try:
    fabfile
except NameError:
    print __doc__
    sys.exit(-1)

app = Flask(__name__)

@app.route("/deploy", methods=["POST"])
def deploy():
    # we only deploy when push to origin/master
    subprocess.call(["fab", "-f", fabfile, "deploy"])
    return "ok"

app.run(host=host, port=port)
