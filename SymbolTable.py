class SymbolTable:
    
    def __init__(self, *args, **kwargs):
        self.classTable = {}
        self.indices = {'field':0, 'static':0, 'local':0, 'argument':0}
        self.subRoutineTable = {}

    def startSubroutine(self):
        self.subRoutineTable = {}
        self.indices['local'] = 0
        self.indices['argument'] = 0

    def define(self, name, varType, kind):
        if kind in ('field', 'static', 'local', 'argument'):
            if kind in ('field', 'static'):
                self.classTable[name] = [varType, kind, self.indices[kind]]
            elif kind in ('local', 'argument'):
                self.subRoutineTable[name] = [varType, kind, self.indices[kind]]
            self.indices[kind] += 1

    def VarCount(self, kind):
        return self.indices[kind]

    def KindOf(self, name):
        if name in self.subRoutineTable:
            return self.subRoutineTable[name][1]
        elif name in self.classTable:
            return self.classTable[name][1]
        else:
            return None

    def TypeOf(self, name):
        if name in self.subRoutineTable:
            return self.subRoutineTable[name][0]
        elif name in self.classTable:
            return self.classTable[name][0]
        else:
            return None

    def IndexOf(self, name):
        if name in self.subRoutineTable:
            return self.subRoutineTable[name][2]
        elif name in self.classTable:
            return self.classTable[name][2]
        else:
            return None

