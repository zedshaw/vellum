# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.


"""Vellum is a build tool similar in spirit to Make, Rake, and
Scons but with a separation of the build description and the 
processing."""

class DieError(Exception): 
    """
    Used by everything to abort processing.
    Tracks targets and line numbers for the user.
    """
    def __init__(self, target, line, cmd, msg):
        self.target = target
        self.line = line
        self.cmd = cmd
        self.message = msg

    def __str__(self):
        return "(%s:%d) failed running %s:\n\t'%s'" % (self.target, 
                self.line, 
                repr(self.cmd), 
                self.message)


class ImportError(Exception): pass

