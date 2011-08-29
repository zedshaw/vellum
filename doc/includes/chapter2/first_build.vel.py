options(default "hello")

imports[] 

depends()

targets(
    hello 
        $ echo 'hi'
)

### @export "depends"
options(default "hello")

imports[] 

depends(
    hello ['py.hello']
)

targets(
    hello 
        $ echo 'hi'

    py.hello py "print 'hello from python'"
)

### @export "targets"
options(default "hello")

imports[] 

depends(
    hello ['py.hello']
)

targets(
    hello [
        $ echo 'hi'
        $ echo 'hello again'
        $ date
    ]

    py.hello [
        py [ 
            |print 'hello from python'
            |print globals()
        ]
        $ echo "i'm a shell command"
    ]
)
