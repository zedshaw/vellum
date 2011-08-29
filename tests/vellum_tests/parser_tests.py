# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

import vellum.parser
from nose.tools import *

def parse(what, s):
    """This adds the \0 terminator for the parser."""
    return vellum.parser.parse(what, s + "\0")

def parse_file(file):
    f = open(file,'r')
    return parse('input', f.read())

def test_parse_input():
    spec = parse_file("build.vel")
    assert "targets" in spec
    assert "imports" in spec
    assert "depends" in spec
    assert "options" in spec

def test_parse_assignment():
    cases = [
            "random()",
            "targets(test 1)",
            "targets(test 2)\nstuff(test 3)"
            ]
    for case in cases:
        assert parse("input", case)

def test_parse_expr():
    cases = {
            "(test [1 2 3 4])": {'test' : [1,2,3,4]},
            "[1 2 3 4 5]": [1,2,3,4,5],
            "[(test 1) [1 2]]": [{'test': 1}, [1,2]],
            "12345": 12345,
            "'testing'": 'testing',
            "$ a shell\n": ' a shell\n',
            }

    for case, result in cases.items():
        p = parse("expr", case)
        assert_equal(p, result, "Expression %r did not parse to match, but was %r." % (case, result))

def test_parse_reference():
    cases = {
            "name1 'hi'": 
                vellum.parser.Reference("name1", 'hi'),
            "name3 [1 2 3]": 
                vellum.parser.Reference("name3", [1,2,3]),
            "name4 (test 1)":
                vellum.parser.Reference("name4", {'test': 1}),
    }

    for case,compare in cases.items():
        res = parse('reference', case)
        assert res, "Reference %s did not parse." % case
        assert_equal(compare.name, res.name, "name %s should be %s" % (compare.name, res.name))
        assert_equal(compare.expr, res.expr, "name %s should be %s" % (compare.name, res.name))



