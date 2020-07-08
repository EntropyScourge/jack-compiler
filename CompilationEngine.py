import JackTokenizer
import SymbolTable
import VMWriter

class CompilationEngine:
    def __init__(self, inputString, outputFile):
        self.tk = JackTokenizer.JackTokenizer(inputString)
        self.st = SymbolTable.SymbolTable()
        self.vt = VMWriter.VMWriter()
        self.outputString = ''
        self.outputFile = outputFile
        self.compClassDict = {'field':self.compileClassVarDec, 'static':self.compileClassVarDec, 'constructor':self.compileSubroutineDec, 
        'function':self.compileSubroutineDec, 'method':self.compileSubroutineDec}
        self.compStatementDict = {'let':self.compileLet, 'if':self.compileIf, 'while':self.compileWhile, 'do':self.compileDo, 'return':self.compileReturn}
        self.compTokenDict = {'symbol':self.tk.symbol, 'keyword':self.tk.keyword, 'identifier':self.tk.identifier, 'integerConstant':self.tk.intVal, 'stringConstant':self.tk.stringVal}
        self.XMLSymDict = {'<':'&lt;', '>':'&gt;', '&':'&amp;', '"':'&quot'}
        self.opDict = {'+':'ADD', '-':'SUB', '&':'AND', '|':'OR', '<':'LT', '>':'GT', '=':'EQ'}
        self.sysDict = {}
        self.multiTermExpression = False
        self.indent = ''
        self.nArgs = 0
        self.voidMethod = False

    def compileClass(self): # 'class' className '{' classVarDec* subroutineDec* '}'
        #self.outputString += '<tokens>\n'
        
        #'class'
        self.outputString += self.indent + '<class>\n'
        self.addIndent()
        self.process('keyword', 'class')
        
        #className
        self.process('identifier', kind='class')
        self.className = self.tk.identifier()
        
        #'{'
        self.process('symbol', '{')
        self.tk.advance()
        
        while not (self.tk.tokenType() == 'symbol' and self.tk.symbol() == '}'):
            self.process('keyword', self.compClassDict.keys(), advance=False, xmlOut=False)
            self.compClassDict[self.tk.keyword()]()

        #'}
        self.process('symbol', '}', advance=False)
        self.removeIndent()
        self.outputString += self.indent + '</class>\n'
        #self.outputString += '</tokens>\n'

    def compileClassVarDec(self, advance=False): # ('static'|'field') type varName (',' varName )* ';'
        
        self.outputString += self.indent + '<classVarDec>\n'
        self.addIndent()
        
        #static or field
        self.process('keyword', ['field', 'static'], advance=advance)
        kind = self.tk.keyword()
        
        #type declaration
        self.process(['keyword', 'identifier'], ['void', 'int', 'char', 'boolean'])
        VarType = self.tk.currentToken
        
        #variable declarations
        while not (self.tk.tokenType() == 'symbol' and self.tk.symbol() == ';'):
            self.process('identifier', kind=kind, varType=VarType)
            self.process('symbol',[',', ';'])
        self.tk.advance()
        
        self.removeIndent()
        self.outputString += self.indent + '</classVarDec>\n'
        
    def compileSubroutineDec(self): # ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        self.ifLabels = 0
        self.whileLabels = 0
        
        self.outputString += self.indent + '<subroutineDec>\n'
        self.addIndent()

        #subroutine keyword
        self.process('keyword', ['constructor', 'function', 'method'], advance=False)
        subRoutineType = self.tk.keyword()

        #type declaration
        self.process(['keyword', 'identifier'], ['void', 'int', 'char', 'boolean'])
        
        #subroutineName
        self.process('identifier', kind='subroutine')
        self.funcName = self.className + "." + self.tk.identifier()
        
        # ( parameterList )
        self.process('symbol', '(')
        self.compileParameterList(subRoutineType)
        self.process('symbol', ')', advance=False)

        if self.tk.keyword() == 'void': self.voidMethod = True
        else: self.voidMethod = False
        
        #subroutineBody
        self.compileSubroutineBody(subRoutineType)
        
        self.removeIndent()
        self.outputString += self.indent + '</subroutineDec>\n'

    def compileParameterList(self, subRoutineType):
        self.st.startSubroutine()
        if subRoutineType == 'method':
            self.st.define('this', self.className, 'argument')
        self.outputString += self.indent + '<parameterList>\n'
        self.addIndent()
        self.tk.advance()
        nParams = 0
        if self.tk.symbol() != ')':
            self.process(['keyword', 'identifier'], ['int', 'char', 'boolean'], advance=False)
            self.process('identifier', kind='argument')
            nParams = 1
            self.tk.advance()
            while not (self.tk.tokenType() == 'symbol' and self.tk.symbol() == ')'):
                self.process('symbol', ',', advance=False)
                self.process(['keyword', 'identifier'], ['int', 'char', 'boolean'], kind='object')
                self.process('identifier', kind='argument')
                nParams += 1
                self.tk.advance()
                
        self.removeIndent()
        self.outputString += self.indent + '</parameterList>\n'
        
    def compileSubroutineBody(self, subRoutineType):
        self.outputString += self.indent + '<subroutineBody>\n'
        self.addIndent()
        
        self.process('symbol', '{')
        self.tk.advance()
        self.nVars = 0
        while self.tk.tokenType() == 'keyword' and self.tk.keyword() == 'var':
            self.compileVarDec()
            self.tk.advance()

        self.vt.writeFunction(self.funcName, self.nVars)

        if subRoutineType == 'constructor':
            self.vt.writePush('constant', self.st.VarCount('field'))
            self.vt.writeCall('Memory.alloc', 1)
            self.vt.writePop('pointer', 0)
        elif subRoutineType == 'method':
            self.vt.writePush('argument', 0)
            self.vt.writePop('pointer', 0)
        
        self.compileStatements()
        self.process('symbol','}', advance=False)
        self.tk.advance()
        
        self.removeIndent()
        self.outputString += self.indent + '</subroutineBody>\n'        

    def compileVarDec(self):
        self.outputString += self.indent + '<varDec>\n'
        self.addIndent()
        
        self.process('keyword', 'var', advance=False)
        self.process(['keyword', 'identifier'], ['int', 'char', 'boolean'], kind='class')
        while True:
            self.process('identifier', kind='local')
            self.nVars += 1
            self.process('symbol', [',', ';'])
            if self.tk.tokenType() == 'symbol' and self.tk.symbol() == ';':
                break
                
        self.removeIndent()
        self.outputString += self.indent + '</varDec>\n'

    def compileStatements(self):
        self.outputString += self.indent + '<statements>\n'
        self.addIndent()
        
        while not (self.tk.tokenType() == 'symbol' and self.tk.symbol() == '}'):
            self.process('keyword', ['let', 'if', 'while', 'do', 'return'], advance=False, xmlOut=False)
            self.compStatementDict[self.tk.keyword()]()
            
        self.removeIndent()
        self.outputString += self.indent + '</statements>\n'
    
    def compileLet(self):
        self.outputString += self.indent + '<letStatement>\n' + self.indent + '<keyword> let </keyword>\n'
        self.addIndent()
        
        self.process('identifier')
        var = self.tk.identifier()
        self.process('symbol', ['=', '['])
        if self.tk.symbol() == '[':
            self.vt.writePush(self.st.KindOf(var), self.st.IndexOf(var))
            self.compileExpression()
            self.vt.WriteArithmetic('ADD')
            self.process('symbol', ']', advance=False)
            self.process('symbol', '=')
            self.compileExpression()
            self.vt.writePop('temp', '0')
            self.vt.writePop('pointer', '1')
            self.vt.writePush('temp', '0')
            self.vt.writePop('that', '0')
        else:
            self.compileExpression()
            self.vt.writePop(self.st.KindOf(var), self.st.IndexOf(var))
        self.process('symbol', ';', advance=False)
        self.tk.advance()
        
        self.removeIndent()
        self.outputString += self.indent + '</letStatement>\n'        

    def compileIf(self):
        self.outputString += self.indent + '<ifStatement>\n'
        self.addIndent()
        
        self.outputString += self.indent + '<keyword> if </keyword>\n'
        self.process('symbol', '(', advance=True)
        self.compileExpression()
        self.vt.WriteArithmetic('NOT')
        Label1 = 'IF_TRUE' + str(self.ifLabels)
        self.vt.WriteIf(Label1)
        Label2 = 'IF_FALSE' + str(self.ifLabels)
        #self.vt.WriteGoto(Label2)
        #Label3 = 'IF_END' + str(self.ifLabels)
        self.ifLabels += 1
        self.process('symbol', ')', advance=False)
        self.process('symbol', '{')
        self.tk.advance()
        #self.vt.WriteLabel(Label1)
        self.compileStatements()
        #self.vt.WriteGoto(Label3)
        self.process('symbol', '}',advance=False)
        self.tk.advance()
        self.checkType(['keyword','symbol'], 'expected an else or another statement')
        #self.vt.WriteLabel(Label2)
        if self.tk.tokenType() == 'keyword' and self.tk.keyword() == 'else':
            self.vt.WriteGoto(Label2)
            self.vt.WriteLabel(Label1)
            self.outputString += self.indent + '<keyword> else </keyword>\n'
            self.process('symbol', '{')
            self.tk.advance()
            self.compileStatements()
            self.vt.WriteLabel(Label2)
            self.process('symbol', '}', advance=False)
            self.tk.advance()
        else: self.vt.WriteLabel(Label1)
        #self.vt.WriteLabel(Label3)
            
        self.removeIndent()
        self.outputString += self.indent + '</ifStatement>\n'
        
    def compileWhile(self):
        self.outputString += self.indent + '<whileStatement>\n'
        self.addIndent()
        
        self.outputString += self.indent + '<keyword> while </keyword>\n'
        self.process('symbol', '(')
        Label1 = 'WHILE_EXP' + str(self.whileLabels)
        self.vt.WriteLabel(Label1)
        Label2 = 'WHILE_END' + str(self.whileLabels)
        self.whileLabels += 1
        self.compileExpression()
        self.vt.WriteArithmetic('NOT')
        self.vt.WriteIf(Label2)
        self.process('symbol', ')', advance=False)
        self.process('symbol', '{')
        self.tk.advance()
        self.compileStatements()
        self.vt.WriteGoto(Label1)
        self.vt.WriteLabel(Label2)
        self.process('symbol', '}' , advance=False)
        self.tk.advance()
        
        self.removeIndent()
        self.outputString += self.indent + '</whileStatement>\n'

    def compileDo(self, *args):
        self.outputString += self.indent + '<doStatement>\n'
        self.addIndent()
        
        self.process('keyword', 'do', advance=False)
        self.process('identifier', ' a class or subroutine name', kind='subroutine', xmlOut=False)
        self.process('symbol', ['(','.'], xmlOut=False)
        if self.tk.symbol() == '.':
            objectName = self.tk.identifier()
            className = self.st.TypeOf(objectName)
            if className == None: className = objectName
            else: self.vt.writePush(self.st.KindOf(objectName), self.st.IndexOf(objectName))
        else:
            className = self.className
            objectName = None
        self.outputString += self.indent + '<identifier kind=' + {'(':'subroutine', '.':'class'}[self.tk.symbol()] + '>' + self.tk.previousToken() + '</identifier>\n'
        self.outputString += self.indent + '<symbol>' + self.tk.symbol() + '</symbol>\n'
        self.compileCall(True, className, objectName)
        self.vt.writePop('temp', 0)
        self.process('symbol', ';')
        self.tk.advance()
        
        self.removeIndent()
        self.outputString += self.indent + '</doStatement>\n'

    def compileCall(self, advance, className, objectName):
        self.nArgs = 0
        if self.tk.symbol() == '(':
            funcName = self.tk.previousToken()
            self.vt.writePush('pointer', 0)
            self.compileExpressionList()
            self.nArgs += 1
        elif self.tk.symbol() == '.':
            self.process('identifier', 'a subroutine name', kind='subroutine')
            funcName = self.tk.identifier()
            self.process('symbol', '(')
            self.compileExpressionList()
        self.process('symbol', ')', advance=False)
        if objectName in self.st.classTable or objectName in self.st.subRoutineTable:
            self.nArgs += 1
        self.vt.writeCall(className + '.' + funcName, str(self.nArgs))

    def compileReturn(self):
        self.outputString += self.indent + '<returnStatement>\n'
        self.addIndent()
        
        self.process('keyword', 'return', advance=False)
        self.tk.advance()
        if self.tk.keyword() == 'this':
            self.vt.writePush('pointer', 0)
            self.tk.advance()
        elif not (self.tk.tokenType() == 'symbol' and self.tk.symbol() == ';'):
            self.compileExpression(False)
        else:
            self.vt.writePush('constant', 0)
        self.vt.writeReturn()
        self.process('symbol', ';', advance=False)
        self.tk.advance()
        
        self.removeIndent()
        self.outputString += self.indent + '</returnStatement>\n'

    def compileExpression(self, advance=True):
        self.outputString += self.indent + '<expression>\n'
        self.addIndent()
        
        self.multiTermExpression = False
        self.compileTerm(advance)
        if self.tk.tokenType() == 'symbol' and self.tk.symbol() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            while True:
                self.multiTermExpression = True
                self.process('symbol', ['+', '-', '*', '/', '&', '|', '<', '>', '='], advance=False)
                op = self.tk.symbol()
                self.compileTerm()
                if op in ['*', '/']:
                    self.vt.writeCall({'*':'Math.multiply', '/':'Math.divide'}[op], 2)
                else:
                    self.vt.WriteArithmetic(self.opDict[op])
                if self.tk.symbol() not in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
                    break
                    
        self.removeIndent()
        self.outputString += self.indent + '</expression>\n'

    def compileTerm(self, advance=True):
        self.outputString += self.indent + '<term>\n'
        self.addIndent()
        
        className = ''
        self.process(['integerConstant', 'stringConstant', 'keyword', 'identifier', 'symbol'], ['true', 'false', 'null', 'this', '(', '-', '~'], advance=advance, xmlOut=False)
        if self.tk.tokenType() is not 'identifier':
            self.outputString += self.indent + '<'+self.tk.tokenType() + '>' + self.tk.currentToken + '</' + self.tk.tokenType()+ '>\n'
        if self.tk.tokenType() == 'integerConstant':
            self.vt.writePush('constant', self.tk.intVal())
        if self.tk.tokenType() == 'stringConstant':
            self.vt.writePush('constant', len(self.tk.stringVal()))
            self.vt.writeCall('String.new', 1)
            for i in range(len(self.tk.stringVal())):
                self.vt.writePush('constant', ord(self.tk.stringVal()[i]))
                self.vt.writeCall('String.appendChar', 2)
        if self.tk.tokenType() == 'keyword':
            if self.tk.keyword() in ['false','null']:
                self.vt.writePush('constant', 0)
            if self.tk.keyword() == 'true':
                self.vt.writePush('constant', 1)
                self.vt.WriteArithmetic('NEG')
            if self.tk.keyword() == 'this': self.vt.writePush('pointer', 0)
            self.tk.advance()
        if self.tk.tokenType() == 'symbol':
            previousTokenType = self.tk.tokenType()
            if self.tk.symbol() in ['-', '~']: #unaryOp term
                sym = self.tk.symbol()
                self.compileTerm()
                self.vt.WriteArithmetic({'-':'NEG', '~':'NOT'}[sym])
            elif self.tk.symbol() == '(': #(expression)
                self.compileExpression()
                self.process('symbol', ')', advance=False)
                self.tk.advance()
        else:
            previousTokenType = self.tk.tokenType()
            self.tk.advance()
        if self.tk.tokenType() == 'symbol' and self.tk.symbol() in ['[', '(', '.']:
            if self.tk.symbol() == '[':
                self.outputString += self.indent + '<identifier kind=Array>' + self.tk.previousToken() + '</identifier>\n'
                self.vt.writePush(self.st.KindOf(self.tk.identifier()), self.st.IndexOf(self.tk.identifier()))
                self.process('symbol', '[', advance=False)
                self.compileExpression()
                self.vt.WriteArithmetic('ADD')
                self.vt.writePop('pointer', '1')
                self.vt.writePush('that', '0')
                self.process('symbol', ']', advance=False)
            else:
                if self.tk.symbol() == '.':
                    objectName = self.tk.identifier()
                    className = self.st.TypeOf(objectName)
                    if objectName in self.st.classTable or objectName in self.st.subRoutineTable:
                        self.vt.writePush(self.st.KindOf(objectName), self.st.IndexOf(objectName))
                    if className is None: className = objectName
                else:
                    objectName = None
                    className = self.className
                self.compileCall(True, className, objectName)
            self.tk.advance()
        elif previousTokenType is 'identifier':
            self.vt.writePush(self.st.KindOf(self.tk.previousToken()), str(self.st.IndexOf(self.tk.previousToken())))
            
        self.removeIndent()
        self.outputString += self.indent + '</term>\n'
        
    def compileExpressionList(self):
        self.outputString += self.indent + '<expressionList>\n'
        self.addIndent()
        
        self.tk.advance()
        if self.tk.symbol() != ')':
            self.compileExpression(False)
            self.nArgs = 1
            while self.tk.symbol() == ',':
                self.process('symbol', ',', advance=False)
                self.compileExpression()
                self.nArgs += 1
            
        self.removeIndent()
        self.outputString += self.indent + '</expressionList>\n'

    def checkToken(self, token, expectedTokens, message = ''):
        if token not in expectedTokens:
            raise ValueError(message)
        else:
            pass
    
    def checkType(self, expectedTypes, message):
        if self.tk.tokenType() not in expectedTypes:
            print(self.outputString)
            print(self.tk.currentToken, self.tk.currentID)
            raise TypeError(message)
        else:
            pass
            
    def addIndent(self):
        self.indent += '  '
        
    def removeIndent(self):
        self.indent = self.indent[:len(self.indent)-2]

    def process(self, expectedTypes, expectedTokens='', kind = None, varType='None', advance=True, xmlOut = True):
        xmlAttr = ''
        if advance:
            self.tk.advance()
        self.checkType(expectedTypes, 'Expected '+' or '.join(expectedTypes) + ', got ' + self.tk.tokenType() + ' instead' if isinstance(expectedTypes, list) else 'Expected '+ expectedTypes + ', got ' + self.tk.tokenType() + ' instead')
        token = self.compTokenDict[self.tk.tokenType()]()
        if self.tk.tokenType() in ['symbol', 'keyword']:
            self.checkToken(token, expectedTokens, 'Expected '+' or '.join(expectedTokens) + ', got ' + self.tk.currentToken + ' instead')
        elif self.tk.tokenType() == 'identifier':
            if self.st.KindOf(self.tk.identifier()) is None:
                self.st.define(self.tk.identifier(), varType=self.tk.previousToken(), kind=kind)
            else:
                kind = self.st.KindOf(self.tk.identifier())
            if kind is not None: xmlAttr = ' kind=' + kind
            if kind in ['field', 'static', 'local', 'argument']:
                xmlAttr += ' index=' + str(self.st.IndexOf(self.tk.identifier()))
            if varType is None:
                varType = self.tk.identifier()
        if xmlOut:
            if self.tk.currentToken in self.XMLSymDict:
                self.outputString += self.indent + '<'+self.tk.tokenType()+ xmlAttr +'>'+self.XMLSymDict[token]+'</'+self.tk.tokenType()+'>\n'
            else:
                self.outputString += self.indent + '<'+self.tk.tokenType()+ xmlAttr + '>'+token+'</'+self.tk.tokenType()+'>\n'

    def writeOutput(self):
        open(self.outputFile, 'w').writelines('\n'.join(self.vt.output))
        