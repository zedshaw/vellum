# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from nose.tools import *
from vellum.scribe import Scribe
from vellum.script import Script
import vellum
from vellum.parser import Reference
import os

def setup():
    global scribe
    scribe = Scribe(Script("build"))
    assert scribe.script

def test_option():
    assert scribe.option("setup")
    assert not scribe.option("not valid")

def test_log():
    scribe.log("testing 1 2 3")

def test_die():
    try:
        scribe.target = "test_target"
        scribe.die("testing cmd", "test message")
    except vellum.DieError, err:
        assert err.target == "test_target"
        assert err.line == 1
        assert err.cmd == "testing cmd"
        assert err.message == "test message"

    scribe.options["keep_going"] = True
    scribe.die("testing cmd", "this is a message")

def test_parse_target():
    body = [' bzr log --short > CHANGES', 
            '', 
            ' bzr commit', 
            '', 
            ' bzr push', '']

    # commit is a list of strings
    assert_equal(body, scribe.parse_target(body))

    # a long string becomes a list of strings
    assert_equal(body, scribe.parse_target("\n".join(body)))

    # a single reference becomes a list of references len 1
    reference = Reference('test','hello')
    assert_equal([reference], scribe.parse_target(reference)) 

def test_body_of_target():
    # and now make sure that it blows up
    assert_raises(KeyError, scribe.body_of_target, "not here")

    # valid ones should return something
    assert scribe.body_of_target("book.draft")

    # dependency only targets should throw an error not being real
    assert_raises(KeyError, scribe.body_of_target, "build")

def test_execute():
    assert scribe.line == 1, "line number not set right: %d" % scribe.line
    scribe.execute([Reference("py", "print 'fuck'")])
    assert scribe.line == 2, "execute of python didn't work: %d" % scribe.line
    scribe.execute(["echo 'test' > /dev/null"])
    assert scribe.line == 3, "execute of shell didn't work: %d" % scribe.line

    scribe.execute([Reference("py", "")] * 10)
    assert scribe.line == 13, "execute of lots of empty python didn't work: %d" % scribe.line

    scribe.execute("echo 'test' > /dev/null\necho 'hi' > /dev/null")
    assert scribe.line == 15, "execute multi-line string didn't work: %d" % scribe.line
    
def test_is_target():
    assert scribe.is_target("sample.commands")
    assert not scribe.is_target("not here")

def test_is_command():
    for name in ["log", "gen", "mkdirs", "install"]:
        assert scribe.is_command(name)
        assert not scribe.is_command("not here" + name)

def test_command():
    """More complete command tests are actually in command_tests.py"""
    assert not scribe.command("log", "this is a test")

def test_modules():
    assert scribe.is_command("log")
    assert not scribe.command("log", "test logging")

def test_push_pop_scope():
    orig = scribe.options.copy()
    scribe.push_scope({"test": 1})
    assert not orig==scribe.options, "pushing scope didn't change it."
    assert len(scribe.stack) == 1
    assert scribe.stack[0] == orig
    scribe.pop_scope()
    assert orig==scribe.options, "popping should bring orig back"

def test_interpolate():
    assert scribe.interpolate("test", "%(setup)s") == repr(scribe.options["setup"])

def test_transition():
    scribe.transition("testing.noop")

def test_build():
    scribe.build(["testing.noop"])
