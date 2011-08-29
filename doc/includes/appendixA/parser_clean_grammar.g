rule input: (reference | COMMENT LINE)* ENDMARKER 
rule expr: atom | reference | structure 
rule reference: NAME expr 
rule atom: NUMBER  | STRING | SH LINE 
rule structure: 
    LSQB elements? RSQB 
    | LPAR dictmaker? RPAR 
rule elements: (expr)+ 
rule dictmaker: (reference)+ 
