# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from nose.tools import *
from vellum.script import Script

def test_configure():
    script = Script("build")
    assert script.options
    assert script.targets
    assert script.depends

def test_resolve_depends():
    script = Script("build")
    for target in script.targets:
        assert target in script.resolve_depends(target)

def test_show():
    script = Script("build")
    script.show()

def test_resolve_targets():
    script = Script("build")
    build = script.resolve_targets(["build"])
    default = script.resolve_targets()
    assert_equal(default, ['parser', 'testing.run', 'tests'])
    assert len(build) > 0
    assert 'build' in build
    assert 'tests' in build

