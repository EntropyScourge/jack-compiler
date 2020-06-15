class VMWriter:
    def __init__(self):
        self.arithDict = {'ADD':'add', 'SUB':'sub', 'NEG':'neg', 'EQ':'eq', 'GT':'gt', 'LT':'lt', 'AND':'and', 'OR':'or', 'NOT':'not'}
        self.output = []

    def writePush(self, segment, index):
        if index is None:
            segment = 'constant'
            index = 0
        if segment == 'field':
            segment = 'this'
        self.output.append('push ' + segment + ' ' + str(index))

    def writePop(self, segment, index):
        if segment == 'field':
            segment = 'this'
        self.output.append('pop ' + segment + ' ' + str(index))

    def WriteArithmetic(self, command):
        self.output.append(self.arithDict[command])

    def WriteLabel(self, label):
        self.output.append('label ' + label)

    def WriteGoto(self, label):
        self.output.append('goto ' + label)

    def WriteIf(self, label):
        self.output.append('if-goto ' + label)

    def writeCall(self, name, nArgs):
        self.output.append('call ' + name + ' ' + str(nArgs))

    def writeFunction(self, name, nLocals):
        self.output.append('function ' + name + ' ' + str(nLocals))

    def writeReturn(self):
        self.output.append('return')

    def close(self):
        return self.output
