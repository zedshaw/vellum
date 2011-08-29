# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from vellum import DieError
from vellum.parser import Reference
import os
import sys

### @export "class Scribe"
class Scribe(object):
    """
    Turns a build spec into something that can actually run.  Scribe
    is responsible for taking the results from Script and loading
    the extra commands out of ~/.vellum/modules so that you can run
    it.

    This is the equiv. of the component in an interpreter that
    processes a cleaned and structured AST to execute it.
    """

    def __init__(self, script):
        self.script = script
        self.options = self.script.options
        self.target = None
        self.line = 1
        self.source = os.path.expanduser("~/.vellum/modules")
        self.stack = []
        self.commands = self.script.commands

    ### @export "support methods"
    def option(self, name):
        """Tells if there's an option of this type."""
        return self.options.get(name,None)

    def log(self, msg):
        """
        Logs a message to the screen, but only if "verbose"
        option (not quiet).
        """
        if self.option("verbose"): 
            print msg
            sys.stdout.flush()

    def die(self, cmd, msg=""):
        """
        Dies with an error message for the given command listing 
        the target and line number in that target.
        """
        if not self.option("keep_going"):
            raise DieError(self.target, self.line, cmd, msg)

    ### @export "handling targets"
    def body_of_target(self, name):
        """Just gets the target out of the script, returning the
        body.""" 
        return self.script.targets[name]

    def parse_target(self, cmds):
        """
        Takes the body of a target and figures out how to split it
        up so that you can execute it.
        """
        if isinstance(cmds, list):
            return cmds  # lists of stuff are just fine
        elif isinstance(cmds, Reference):
            return [cmds]  # gotta put single references into a list
        elif isinstance(cmds, basestring):
            return cmds.split("\n") # convert big strings into lists of command shells
        else:
            self.die("parse_target", "Definition of target isn't a list, command, or string.")
            return []  # needed in case -k is given

    def is_target(self, target):
        """
        Determines if this is a real target we can transition to, 
        not a virtual one only found in the dependency graph.
        """
        return (target in self.script.targets 
                and self.script.targets[target])

    ### @export "handling commands"
    def is_command(self, name):
        """Tells the scribe if this name is an actual command."""
        return callable(self.commands.get(name, None))

    def command(self, name, expr):
        """
        Runs the command for the given name.  Pulls it out of the
        self.commands.  Normally it just passes expr to the 
        command, but if expr is a dict then it will call it
        with **expr so you can do simpler kword commands.  If
        you don't want this then you just define your command as
        taking **args.
        """
        try:
            to_call = self.commands[name]
        except KeyError, err:
            self.die(name, "Invalid command name %s, use -C to find out what's available.")

        if isinstance(expr, dict):
            return to_call(self, **expr)
        else:
            return to_call(self, expr)


    ### @export "execute target body"
    def execute(self, body):
        """
        Executes the body which can be anything parse_target() can
        handle.  It properly handles the difference between a plain
        string (shell command(s)) or a Reference (do some command),
        or a list of those two.  Assumes you call self.start_target()
        """
        for cmd in self.parse_target(body):
            if "__builtins__" in self.options:
                self.die(cmd, "Your command leaked __builtins__."
                         "Use scribe.push_scope and "
                         "scribe.pop_scope.")

            self.line += 1
            if isinstance(cmd, Reference):
                # Reference objects are indications to run some 
                # Python command rather than a shell.
                if self.is_command(cmd.name):
                    # discontinue on True
                    if self.command(cmd.name, cmd.expr): 
                        self.log("<-- %s" % cmd)
                        return
                else:
                    self.die(cmd, 
                            "Invalid command reference, available "
                            "commands are:\n%r." % 
                            sorted(self.commands.keys()))
            else:
                # it's just shell
                cmd = cmd.strip()
                if cmd: self.command("sh", cmd)

    ### @export "transition to target"
    def transition(self, target):
        """
        The main engine of the whole thing, it will transition to
        the given target and then process it's commands listed.  It
        properly figures out if this is a command reference or a
        plain string to run as a shell.
        """
        if not self.is_target(target): return
        self.line = 0
        self.target = target
        body = self.body_of_target(target)
        self.execute(body)

    ### @export "running all targets"
    def build(self, to_build):
        """
        Main entry point that resolves the main targets for
        those listed in to_build and then runs the results in order.
        """
        building = self.script.resolve_targets(to_build)
        self.log("BUILDING: %s" % building)
        for target in building:
            self.log("-->: %s" % target)
            self.transition(target)

    ### @export "string handling"
    def interpolate(self, cmd_name, expr):
        """
        Takes a string expression and interpolates it
        using the self.options dict as the % paramter.
        It prints more useful errors than you'd normally
        get from Python.
        """
        err_name = "%s %r" % (cmd_name, expr)
        try:
            return expr % self.options
        except ValueError, err:
            self.die(err_name, "Expression has invalid format: %s" % err)
        except KeyError, err:
            self.die(err_name, "No key %s for format, available keys are: %r" % (err, sorted(self.options.keys())))

    ### @export "scope management"
    def push_scope(self, vars={}):
        """
        Takes the current set of options and pushes it onto
        an internal stack but with the new vars in the
        options for the next command to use.  This
        effectively emulates function call semantics for
        targets.
        """
        self.stack.append(self.options)
        self.options = self.options.copy()
        self.options.update(vars)

    def pop_scope(self):
        """
        Does the inverse of push_scope() recovering
        the previous scope.
        """
        self.options = self.stack.pop()



