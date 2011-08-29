# Copyright (C) 2008 Zed A. Shaw.  Licensed under the terms of the GPLv3.

class Reference(object):
    def __init__(self,name, expr):
        self.name = name
        self.expr = expr

    def __str__(self):
        if self.expr:
            return "%s(%r)" % (self.name, self.expr)
        else:
            return "%s"

    def __repr__(self):
        return "Reference(%r,%r)" % (self.name, self.expr)
### @export "grammar"
        

from string import *
import re
from zapps.rt import *

class ParserScanner(Scanner):
    patterns = [
        ('[\\r\\n \\t]+', re.compile('[\\r\\n \\t]+')),
        ('NUMBER', re.compile('[0-9]+[0-9\\.]*')),
        ('STRING', re.compile('\'([^\\n\'\\\\]|\\\\.)*\'|"([^\\n"\\\\]|\\\\.)*"')),
        ('NAME', re.compile('[a-zA-Z][a-zA-Z\\-_0-9/\\.]+')),
        ('LPAR', re.compile('\\(')),
        ('RPAR', re.compile('\\)')),
        ('LSQB', re.compile('\\[')),
        ('RSQB', re.compile('\\]')),
        ('ENDMARKER', re.compile('\x00')),
        ('SH', re.compile('[>$|]')),
        ('LINE', re.compile('[^\\n\\r]+\\n')),
        ('COMMENT', re.compile('#')),
    ]
    def __init__(self, str):
        Scanner.__init__(self,None,['[\\r\\n \\t]+'],str)

class Parser(Parser):
    def input(self):
        self.data = {}
        while self._peek('COMMENT', 'ENDMARKER', 'NAME') != 'ENDMARKER':
            _token_ = self._peek('COMMENT', 'NAME')
            if _token_ == 'NAME':
                reference = self.reference()
                self.data[reference.name] = reference.expr
            else:# == 'COMMENT'
                COMMENT = self._scan('COMMENT')
                LINE = self._scan('LINE')
        ENDMARKER = self._scan('ENDMARKER')
        return self.data

    def expr(self):
        _token_ = self._peek('NUMBER', 'STRING', 'SH', 'NAME', 'LSQB', 'LPAR')
        if _token_ not in ['NAME', 'LSQB', 'LPAR']:
            atom = self.atom()
            return atom
        elif _token_ == 'NAME':
            reference = self.reference()
            return reference
        else:# in ['LSQB', 'LPAR']
            structure = self.structure()
            return structure

    def reference(self):
        NAME = self._scan('NAME')
        expr = self.expr()
        return Reference(NAME, expr)

    def atom(self):
        _token_ = self._peek('NUMBER', 'STRING', 'SH')
        if _token_ == 'NUMBER':
            NUMBER = self._scan('NUMBER')
            return atoi(NUMBER)
        elif _token_ == 'STRING':
            STRING = self._scan('STRING')
            return eval(STRING)
        else:# == 'SH'
            SH = self._scan('SH')
            LINE = self._scan('LINE')
            return LINE

    def structure(self):
        _token_ = self._peek('LSQB', 'LPAR')
        if _token_ == 'LSQB':
            LSQB = self._scan('LSQB')
            if self._peek('RSQB', 'NUMBER', 'STRING', 'SH', 'NAME', 'LSQB', 'LPAR') != 'RSQB':
                elements = self.elements()
            else:
                elements = None

            RSQB = self._scan('RSQB')
            return elements or []
        else:# == 'LPAR'
            LPAR = self._scan('LPAR')
            if self._peek('RPAR', 'NAME') == 'NAME':
                dictmaker = self.dictmaker()
            else:
                dictmaker = None

            RPAR = self._scan('RPAR')
            return dictmaker or {}

    def elements(self):
        res = []
        while 1:
            expr = self.expr()
            res.append(expr)
            if self._peek('NUMBER', 'STRING', 'SH', 'NAME', 'LSQB', 'LPAR', 'RSQB') not in ['NUMBER', 'STRING', 'SH', 'NAME', 'LSQB', 'LPAR']: break
        return res

    def dictmaker(self):
        res = {}
        while 1:
            reference = self.reference()
            res[reference.name] = reference.expr
            if self._peek('NAME', 'RPAR') != 'NAME': break
        return res


def parse(rule, text):
    P = Parser(ParserScanner(text))
    return wrap_error_reporter(P, rule)



### @end

### @export "footer"
if __name__ == '__main__':
    from sys import argv, stdin
    if len(argv) >= 2:
        if len(argv) >= 3:
            f = open(argv[2],'r')
        else:
            f = stdin
        print parse(argv[1], f.read() + "\0")
    else: print 'Args:  <rule> [<filename>]'
