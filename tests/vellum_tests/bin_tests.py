# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from nose.tools import *
from vellum.bin import *
import os

def options_and_script(argv, needs_option):
    options, args = parse_sys_argv(argv)
    assert options[needs_option]
    return options, Script(options["filename"], options)

def test_parse_sys_argv():
    cases = [
        ["-f", "build"],
        ["-q"], ["--quiet"],
        ["-d"], ["--dry-run"],
        ["-k"], ["--keep-going"],
        ["-T"], ["--targets"],
        ["-F"], ["--force"],
        ["-D"], ["--dump"],
        ["-s"], ["--shell"],
        ["-I"], ["--install"],
        ["-S"], ["--search"],
        ["-w", "build.vel"], ["--watch", "build.vel"],
    ]
    assert all([parse_sys_argv(case) for case in cases])


def test_show_targets():
    options, script = options_and_script(["-T"], "show_targets")
    show_targets(options, script)

def test_dump():
    options, ignored = options_and_script(["-D"], "dump")
    dump(options)

def test_install():
    options, script = options_and_script(["-I"], "install")
    install(options, script)
    path = os.path.expanduser("~/.vellum/modules")
    assert os.path.exists(path)
    
def test_shell():
    ### not sure how to test this
    options, script = options_and_script(["-s"], "shell")
    inputs = ["testing.noop"]
    def fake_input():
        try:
            return inputs.pop()
        except IndexError:
            raise EOFError()

    # use the above fake input function to fake out the shell
    shell(options, script, user_input=fake_input)

def test_build():
    options, targets = parse_sys_argv(["testing.noop"])
    script = Script(options["filename"], options)
    build(options, script, targets)

def test_search():
    options, script = options_and_script(["-S"], "search_commands")
    search(options, script, ["echo"])

def test_watch():
    options, script = options_and_script(["-w", "build.vel"], "watch_file")
    watch(options, script, ["echo"], count=1, sleep_time=0)


def test_run():
    cases = [
            ["-f", "build", "--dry-run"],
            ["-q","-d"], ["--dry-run", "--quiet"],
            ["-d"], ["--dry-run"],
            ["-k", "-d"], ["-d", "--keep-going"],
            ["-T"], ["--targets"],
            ["-F", "-d"], ["--dry-run", "--force"],
            ["-D"], ["--dump"],
            ["-I"], ["--install"],
            ]
    for case in cases:
        print "Testing %r" % case
        run(case)

