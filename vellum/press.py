# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

from __future__ import with_statement
from vellum import ImportError
import vellum.parser
import os
import sys
from pprint import pprint

class LoadError(ImportError): pass

### @export "class Press"
class Press(object):
    """
    A Press uses a Parser to read a build spec and then combine it
    with any given import statements.  This is the equiv. of the
    component in a interpreter that builds an AST with the parser.

    The next stage in the processing is for the Script to get the
    Press's results to analyze the contents.
    """

    def __init__(self, main, defaults={}):
        """
        Initializes the press according to the 
        defaults (which come from vellum.bin.parse_sys_argv().
        """
        self.options = defaults
        self.module_source = os.path.expanduser("~/.vellum/modules")
        self.recipe_source =  os.path.expanduser("~/.vellum/recipes")
        self.recipes = {}
        self.modules = {}
        self.main = self.load_recipe(main + ".vel")
        self.main["commands"] = {}
        # we always need these commands
        self.load('module', 'vellum.commands')
        self.imports(self.main)

    ### @export "resolve_vel_file"
    def resolve_vel_file(self, name):
        """
        Tries to find a file ending in .vel with
        the name by first trying in the local directory
        and then in the ~/.vellum/recipes directory.

        It will also add the .vel if one isn't given already.
        """
        if not name.endswith(".vel"): 
            name += ".vel"

        names = (os.path.join(n, name) for n in ["./", self.recipe_source])
        found = [n for n in names if os.path.exists(n)]
        if len(found) == 1:
            return found[0]
        elif len(found) > 1:
            raise LoadError("More than one file named %s: %r." % (name, found))
        else:
            raise LoadError("Did not find file named %s at any of: %r." % (name,
                                                                           found))

    ### @export "load"
    def load(self, kind, file, as_name=None):
        """
        Given a kind of 'recipe' or 'module' this figures out
        how to load the spec or python module.  It will do
        this recursively until it has loaded everything, and
        do it without causing loops.
        """
        if kind == "recipe":
            file = self.resolve_vel_file(file)
            if file not in self.recipes:
                spec = self.load_recipe(file)
                self.join(spec, self.main, file, as_name)
                self.imports(spec)
        elif kind == "module":
            if file not in self.modules:
                cmds = self.load_module(file)
                self.merge(cmds, self.main["commands"], 
                           as_name=as_name)
        else:
            raise ImportError("Invalid kind of import %s, "
                            "use only 'recipe(...)' or "
                            "'module(...)'")

        return self.main

    ### @export "load_recipe"
    def load_recipe(self, file):
        """
        Loads a recipe and then calls self.load to get any
        imports that are defined.
        """
        if file in self.recipes:
            return self.recipes[file]
        else:
            with open(file) as f:
                spec = vellum.parser.parse('input', f.read() + '\0')
                if not spec:
                    raise ImportError("Parser error in file: %s" % file)
                else:
                    return spec

    ### @export "load_module"
    def load_module(self, name):
        """
        Loads a python module and extracts all of the 
        methods that are usable as Vellum commands.
        It returns a dict with the commands.
        """
        if name in self.modules: return self.modules[name]

        sys.path.append(self.module_source)
        mod = __import__(name, globals(), locals())

        # stupid hack to work around __import__ not really importing
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)

        # now module is the actual module we actually requested
        commands = {}
        for k,func in mod.__dict__.items():
            if not k.startswith("_") and hasattr(func, "__call__"):
                commands[k] = func

        sys.path.pop()
        return commands

    ### @export "scope_name"
    def scope_name(self, key, name=None, as_name=None):
        """Does the common name scopings used."""
        name = as_name if as_name else name
        return "%s.%s" % (name, key) if name else key


    ### @export "merge"
    def merge(self, source, target, named=None, as_name=None):
        """
        Takes the source and target dicts and merges
        their keys according to the way scope_name does
        it.  Source is untouched.
        """
        for key,val in source.items():
            target[self.scope_name(key,named,as_name)] = val

    ### @export "join"
    def join(self, source, target, named=None, as_name=None):
        """
        Takes two specs and properly joins them
        using the self.merge() function on all
        of the stanzas.
        """
        # first merge the common dict style stanzas
        for section in ["targets", "options", "depends"]:
            if section in source:
                target.setdefault(section, {})
                self.merge(source[section], 
                           target[section], named, as_name)
    ### @export "imports"
    def imports(self, import_from):
        """
        Goes through the imports listed in import_from
        and then merges them into self.main.
        """
        if not "imports" in import_from: return

        for imp in import_from["imports"]:
            args = imp.expr
            args.setdefault("as", None)
            self.load(imp.name, args["from"], args["as"])

