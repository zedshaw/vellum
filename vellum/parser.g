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
        
%%
parser Parser:
    ignore: r"[\r\n \t]+"
    token NUMBER: "[0-9]+[0-9\.]*"
    token STRING: '\'([^\\n\'\\\\]|\\\\.)*\'|"([^\\n"\\\\]|\\\\.)*"'
    token NAME: r"[a-zA-Z][a-zA-Z\-_0-9/\.]+"
    token LPAR: r'\('
    token RPAR: r'\)'
    token LSQB: r'\['
    token RSQB: r'\]'
    token ENDMARKER: '\0'
    token SH: r'[>$|]'
    token LINE: r'[^\n\r]+\n'
    token COMMENT: '#'

    rule input: 
        {{ self.data = {} }} 
        ( 
         reference {{ self.data[reference.name] = reference.expr }}
         | COMMENT LINE
        )* ENDMARKER 
        {{ return self.data }}

    rule expr: 
            atom {{ return atom }}
            | reference {{ return reference }}
            | structure {{ return structure }}

    rule reference: NAME expr 
        {{ return Reference(NAME, expr) }}

    rule atom: 
        NUMBER {{ return atoi(NUMBER) }} 
        | STRING {{ return eval(STRING) }}
        | SH LINE {{ return LINE }}

    rule structure: 
        LSQB elements? RSQB {{ return elements or [] }} 
        | LPAR dictmaker? RPAR {{ return dictmaker or {} }}

    rule elements: {{res = [] }} (expr {{res.append(expr)}})+ 
        {{ return res }}
    rule dictmaker: {{res = {} }} (reference {{res[reference.name] = reference.expr}})+ 
        {{ return res }}
%%
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
