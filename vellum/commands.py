from __future__ import with_statement
# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

import os
import sys
import fnmatch
import subprocess

def sh(scribe, expr):
    """
    Runs the given list of strings or string as a shell
    command, aborting if the command exits with 0.

    Usage: sh 'echo "test"'
    """
    formatted = scribe.interpolate("sh", "".join(expr))
    scribe.log(" sh: %r" % formatted)
    if not scribe.option("dry_run"):
        retcode = subprocess.call(formatted, 
                shell=True, stderr=1, stdout=1)
                
        if retcode != 0: scribe.die(expr)

def py(scribe, expr):
    """
    Runs the given list of strings or string as a python
    statements.  It doesn't stop, but if you raise an
    exception this will obviously stop the processing.
    You have access to all the options as globals.

    Usage: py 'print "hi"'
    """
    formatted = scribe.interpolate("py", "".join(expr))
    scribe.log(" py: %r" % formatted)
    if not scribe.option("dry_run"):
        scribe.push_scope({"scribe": scribe, "script": scribe.script})
        exec(formatted, globals(), scribe.options)
        scribe.pop_scope()

def log(scribe, expr):
    """
    Logs the string to the user.

    Usage: log "hi there user"
    """
    scribe.log(" " + scribe.interpolate("log", expr))

def needs(scribe, expr):
    """
    Indicates that before this target should continue,
    vellum needs to run the targets in the given list.
    If dependencies for a target don't fit in the main
    listing then use needs to put them in the target.

    Usage: needs ['clean', 'build', 'dist']
    """
    for target in expr:
        if not scribe.is_target(target):
            scribe.die(target, "target %s isn't in the targets list" % target)
        else:
            scribe.transition(target)

def given(scribe, expr, name='given'):
    """
    Evaluates the list of strings or string as a Python
    expression (not statement) and if that expression is
    False stops processing this target.  Read it as:
      given X is True continue.

    Usage: given 'os.path.exists("/etc/passwd")'
    """
    formatted = scribe.interpolate("given", "".join(expr))
    scribe.log(" %s: %r" % (name, formatted))

    if scribe.option("force"): return False
    try:
        return not eval(formatted)
    except Exception, err:
        scribe.die(expr, err)

def unless(scribe, expr):
    """
    The inverse of given, this stops processing
    if the expression is True.  Reads as:
      unless X is False continue.

    Usage: unless 'not os.path.exists("/etc/passwd")'
    """
    if scribe.option("force"): return False
    return not given(scribe, expr, "unless")

def gen(scribe, input=None, output=None, **expr):
    """
    Used to do simple code generation tasks.  It
    expects a "from" and "to" argument in a dict
    then it loads from, string interpolates the
    whole thing against the expr merged with the
    options, and finally writes the results to "to".

    Usage:  gen(input somefile.txt output outfile.txt other "variable")
    """
    scribe.log("gen: input %s output %s" % (input, output) )
    if not (input or output): 
        scribe.die("gen", "You must give both input and output for gen.")

    if scribe.option("dry_run"): return
    expr.update(scribe.options)
    with open(input) as inp:
        with open(output,'w') as out:
            out.write(inp.read() % expr)

def install(scribe, expr):
    """
    Simple command that installs Vellum's ~/.vellum 
    directory for you.  You can also just use: vellum -I.
    WARNING: This might get replaced with something more
    like the install command.

    Usage: install
    """
    # relies on mkdirs to honor dry_run
    mkdirs(scribe, 
           paths=["~/.vellum/modules", "~/.vellum/recipes"], 
           mode=0700)

def mkdirs(scribe, paths=[], mode=0700):
    """
    Takes a dict with "paths" and "mode" and then creates all of those
    paths each with the given mode.  It will also expand user paths
    on each one so you can use the ~ shortcut.

    Usage:  mkdirs(paths ["path1","path2"] mode 0700)
    """
    assert isinstance(paths, list), "mkdirs expects a list as the expression"

    for dir in (os.path.expanduser(p) for p in paths):
        scribe.log(" mkdir: %s" % dir)
        if not (os.path.exists(dir) or scribe.option("dry_run")):
            os.makedirs(dir, mode=0700)

### @export "forall"
def forall(scribe, files=None, do=[], top=".", var="file"):
    """
    Iterates the commands in a do block over all the files
    matching a given regex recursively.  You can put anything
    you'd put in a normal target in the do block to be executed,
    and when it is executed the 'var' variable is set to the
    full path of each file.  This will also be in each task
    you transition to with the 'needs' command.

    forall assumes that you want the variable to be 'file'
    so for most tasks you can leave that option out.  If you
    nest forall expressions then you'll need to give each one
    a different name (just like in a real language).

    Usage: forall(files "*.py" var "file" do [ ... ])
    """
    scribe.log("forall: files %r top %r var %r" % (files, top, var))
    if not files:
        scribe.die("forall", "Must give a file matching "
                   "pattern in parameter 'files'.")

    matches = []
    for path, dirs, fnames in os.walk(top):
        paths = (os.path.join(path,f) for f in fnames)
        matches.extend(fnmatch.filter(paths, files))

    scribe.log("forall: matched %d files." % len(matches))
    for f in matches:
        scribe.push_scope({var: f, "files": matches, "var": var})
        scribe.execute(do)
        scribe.pop_scope()

### @export "cd"
def cd(scribe, to=None, do=[]):
    """
    Temporarily changes to a given directory and then runs the
    block in that directory.  When it's done it pops back to the
    previous directory.
    """
    scribe.log(" cd: %s" % to)
    to = scribe.interpolate("to", to)

    if not to: 
        scribe.die("cd", "Must specify to parameter to cd into.")
    elif not os.path.exists(to):
        scribe.die("cd", "Target chdir path '%s' does not exist." % to)

    curdir = os.path.abspath(os.path.curdir)
    try:
        os.chdir(to)
        scribe.push_scope({"parent": curdir})
        scribe.execute(do)
        scribe.pop_scope()
    finally:
        os.chdir(curdir)

