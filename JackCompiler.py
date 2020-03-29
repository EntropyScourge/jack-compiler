import os
import sys
import CompilationEngine as ce

if os.path.isdir(sys.argv[1]):
    for inputFile in os.listdir(sys.argv[1]):
        if inputFile[-5:] == ".jack":
            print([inputFile])
            source = ce.CompilationEngine(open(sys.argv[1]+inputFile).read(), sys.argv[1]+inputFile[:-4] + 'vm')
            source.compileClass()
            source.writeOutput()

else:
    source = ce.CompilationEngine(open(sys.argv[1]).read(), sys.argv[1][:-4] + 'vm')
    source.compileClass()
    print('Current token is ', source.tk.currentToken)
    source.writeOutput()
    