# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from vellum.press import Press
from nose.tools import *
import sys

def assert_valid(spec):
    tests = [("default","options"),
            ("build","depends"),
            ("sample.commands","targets")]
    for sub,key in tests:
        assert spec[key]
        assert sub in spec[key], "%s not in spec" % repr((sub,key))

def test_resolve_vel_file():
    press = Press("build")
    build = press.resolve_vel_file("build")
    assert_equal(build, "./build.vel")
    build = press.resolve_vel_file("build.vel")
    assert_equal(build, "./build.vel")

    f = open(press.recipe_source + "/" + "test.vel", "w")
    f.write("test")
    f.close()
    test = press.resolve_vel_file("test")
    assert_equal(test, "/home/zedshaw/.vellum/recipes/test.vel")

    test = press.resolve_vel_file("test.vel")
    assert_equal(test, "/home/zedshaw/.vellum/recipes/test.vel")


def test_load():
    press = Press("build")
    assert_valid(press.main)
    print press.main["commands"]
    assert "gen" in press.main["commands"]

def test_load_module():
    press = Press("build")
    commands = press.load_module("vellum.commands")
    assert "~/.vellum/modules" not in sys.path
    assert "gen" in commands
    # make sure that os and others don't show up
    assert "os" not in commands

def test_load_recipe():
    press = Press("build")
    spec = press.load_recipe("scripts/dist.vel")
    assert spec
    assert "imports" in press.main
    assert "targets" in spec

def test_merge():
    source = {"test": 1, "script": 2,
              "depends": 3}
    target = {"test": 4, "notsource": 5}
    start_target = target.copy()
    start_source = source.copy()

    press = Press("build")
    press.merge(source, target, "vellum.test")
    press.merge(source, target)
    press.merge(source, target, named=None, as_name="things")
    press.merge(source, target, named="shittyfucker", as_name="cleanfucker")

    assert_equal(start_source, source)
    assert_not_equal(start_target, target)

    for i in ["cleanfucker", "vellum.test", "things"]:
        assert "%s.test" % i in target

def test_join():
    source = {"targets": {"test": 1, "script": 2,
              "depends": 3}}
    target = {"targets": {"test": 4, "notsource": 5}}
    press = Press("build")

    press.join(source, target)
    press.join(source, target, "vellum.test")
    press.join(source, target, named=None, as_name="things")
    press.join(source, target, "shittyfucker", "cleanfucker")

    print source
    print target

    for i in ["cleanfucker", "vellum.test", "things"]:
        assert "%s.test" % i in target["targets"]
    
