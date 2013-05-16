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
import subprocess
import json
from getopt import getopt
from flask import Flask, request


app = Flask(__name__)

fabfile = "fabfile.py"

@app.route("/deploy", methods=["POST"])
def deploy():
    # we only deploy when push to origin/master
    if json.loads(request.form['payload'])['ref'] == 'refs/heads/master':
	subprocess.call(["fab", "-f", fabfile, "deploy"])
    return "done"

@app.route("/make-test-data")
def make_test_data():
    # we only deploy when push to origin/master
    subprocess.call(["fab", "-f", fabfile, "make_test_data"])
    return "done"

#if __name__ == "__main__":
#    opts, _ = getopt(sys.argv[1:], "f:s:p:h")
#    
#    host = None
#    port = None
#    for o, v in opts:
#        if o == "-s":
#            host = v
#        elif o == "-p":
#            port = int(v)
#        elif o == "-h":
#            print __doc__
#    	sys.exit(-1)
#        elif o == "-f":
#            fabfile = v
#        else:
#            print "unkown option: " + o
#            print __doc__
#            sys.exit(-1)
#    
#    try:
#        fabfile
#    except NameError:
#        print __doc__
#        sys.exit(-1)
#    app.run(host=host, port=port)

