# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from nose.tools import *
from vellum.scribe import Scribe
from vellum.script import Script
import os
import vellum
from vellum.parser import Reference

def setup():
    global scribe
    scribe = Scribe(Script("build"))
    assert scribe.script

def test_system():
    assert scribe.is_command("sh")
    scribe.command("sh", "echo test > /dev/null")

def test_python():
    assert scribe.is_command("py")
    assert not scribe.command("py", "print 'hi'")
    assert not scribe.command("py", ["print 'hi'\n", "print 'line 2'"])

def test_output():
    assert scribe.is_command("log")
    scribe.command("log", "hi")

def test_given():
    # remember, True is returned to indicate stopping
    assert scribe.is_command("given")
    assert not scribe.option("force")  # no force at first

    assert not scribe.command("given", "True")
    assert scribe.command("given", "False")
    scribe.options["force"] = True
    assert not scribe.command("given", "bogus python")
    scribe.options["force"] = False

def test_unless():
    assert scribe.is_command("unless")
    assert not scribe.option("force")  # no force at first

    assert scribe.command("unless", "True")
    assert not scribe.command("unless", "False")
    scribe.options["force"] = True
    assert not scribe.command("unless", "bogus python")
    scribe.options["force"] = True

def test_needs():
    assert scribe.is_command("needs")
    scribe.command("needs", ["testing.noop"])

def test_mkdirs():
    assert scribe.is_command("mkdirs")
    scribe.command("mkdirs", {
        "paths": ["/tmp/testdir", "/tmp/testdir2"],
        "mode": 0744
        })
    assert os.path.exists("/tmp/testdir")
    assert os.path.exists("/tmp/testdir2")

def test_install():
    assert scribe.is_command("mkdirs")
    scribe.command("install", None)
    assert os.path.exists(os.path.expanduser("~/.vellum/modules"))


def test_forall():
    assert scribe.is_command("forall")
    line = scribe.line
    scribe.command("forall", {
        "files": "*.py", 
        "var": "file", 
        "do": [Reference("py", "print 'forall','%(var)s', %(files)r, %(file)r")]})
    assert not scribe.option("files")
    assert not scribe.option("file")
    assert len(scribe.stack) == 0, "scribe stack should be empty"

def test_cd():
    assert scribe.is_command("cd")
    curdir = os.path.abspath(os.curdir)
    scribe.command("cd", {
        "to": "tests",
        "do": [Reference("py", "print 'forall'")]})
    assert_equal(os.path.abspath(os.curdir), curdir)

def test_gen():
    assert scribe.is_command("gen")
    scribe.command("gen", {"input": 'scripts/setup.py', "output": 'tests/genout.py'})
    assert os.path.exists("tests/genout.py")
    os.unlink("tests/genout.py")

