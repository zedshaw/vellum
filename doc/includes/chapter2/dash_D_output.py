{'commands': {...},
 'depends': {'hello': ['py.hello']},
 'imports': [],
 'options': {'default': 'hello'},
 'targets': {
     'hello': [
         " echo 'hi'\n",
         " echo 'hello again'\n", ' date\n'
     ],
     'py.hello': [
         Reference('py',[
             "print 'hello from python'\n", 
             'print globals()\n'
         ]),
         ' echo "i\'m a shell command"\n'
     ]
 }
}
