#!/usr/bin/env python3
"""
This script takes 2-3 args: [--browse] <Doxyfile> <sourcefile>

--browse will open the resulting docs in a web browser.
"""
import sys
import os
import subprocess
import tempfile

def find_gitroot(filepath_reference):
    path = filepath_reference
    path_prev = ""
    while not os.path.exists(os.path.join(path, ".git")) and path != path_prev:
        path_prev = path
        path = os.path.dirname(path)
    return path

def find_doxy(filepath_reference):
    root = find_gitroot(filepath_reference)

    # project specific!
    return os.path.join(root, "doc", "doxygen", "Doxyfile")

sourcefile = sys.argv[-1]

doxyfile = find_doxy(sourcefile)
os.chdir(os.path.dirname(doxyfile))

tempfile = tempfile.NamedTemporaryFile(mode='w+b')
doxyfile_tmp = tempfile.name
tempfile.write(open(doxyfile, "r+b").read())
tempfile.write(b'\n\n')
tempfile.write(b'INPUT=' + os.fsencode(sourcefile) + b'\n')
tempfile.flush()

subprocess.call(("doxygen", doxyfile_tmp))
del tempfile

# Maybe handy, but also annoying?
if "--browse" in sys.argv:
    import webbrowser
    webbrowser.open("html/files.html")
