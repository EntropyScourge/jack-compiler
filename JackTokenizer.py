class JackTokenizer:
    def __init__(self, jackInput):
        self.jackInput = jackInput
        self.keywords = ["class","constructor","function","method","field","static","var","int","char","boolean","void","true","false","null","this","let","do","if","else","while","return"]
        self.symbols = ["{","}","(",")","[","]",".",",",";","+","-","*","/","&","|","<",">","=","~"]
        self.tokenList = []
        self.currentPos = 0
		
    def hasMoreTokens(self):
        if self.currentPos < len(self.jackInput) -1:
            return True
        else:
            return False

    def skipComments(self):
        #removing whitespace and comments
        while self.jackInput[self.currentPos] in [' ', '\n', '	']:
            if self.hasMoreTokens():
                self.currentPos += 1
        if '//' in self.jackInput[self.currentPos:self.currentPos+2]:
            while self.jackInput[self.currentPos] != '\n' and self.hasMoreTokens():
                self.currentPos += 1
            self.currentPos += 1
        elif '/*' in self.jackInput[self.currentPos:self.currentPos+2]:
            self.comment = True
            while '*/' not in self.jackInput[self.currentPos:self.currentPos+2] and self.hasMoreTokens():
                self.currentPos += 1
            self.currentPos += 2
        while self.jackInput[self.currentPos] in [' ', '\n', '	']:
            if self.hasMoreTokens():
                self.currentPos += 1

    def advance(self):
        while self.jackInput[self.currentPos:self.currentPos+2] in ['/*', '//'] or self.jackInput[self.currentPos] in [' ', '\n']:
            self.skipComments()
        #actually tokenizing all the things
        word = ''
        if self.jackInput[self.currentPos] in self.symbols:
            self.currentToken = self.jackInput[self.currentPos].replace('\n','')
            self.currentID = 'symbol'
            word = self.currentToken
            self._symbol = self.currentToken
        else:
            i = 0
            done = False
            inString = False
            while not done:
                word = word + self.jackInput[self.currentPos+i]
                if word.isdigit() and (self.jackInput[self.currentPos+i+1] == ' ' or self.jackInput[self.currentPos+i+1] in self.symbols):
                    self.currentToken = word              
                    self.currentID = 'integerConstant'
                    done = True
                    self._intVal = self.currentToken
                elif self.jackInput[self.currentPos] == '\"':
                    inString = True
                    if self.jackInput[self.currentPos+i+1] == '\"':
                        word = word + '\"'
                        self.currentToken = word
                        self.currentID = 'stringConstant'
                        done = True
                        self._stringVal = self.currentToken[1:-1]
                elif not inString:
                    if self.jackInput[self.currentPos+i+1] == ' ' or self.jackInput[self.currentPos+i+1] in self.symbols:
                        Word = word.replace('\n','')
                        if Word in self.keywords:
                            self.currentID = 'keyword'
                            done = True
                            self._keyword = Word
                        elif Word.isspace():
                            pass
                        else:
                            self.currentID = 'identifier'
                            done = True
                            self._identifier = Word
                        self.currentToken = Word
                i += 1
        self.currentPos += len(word)
        self.tokenList.append(self.currentToken)
        #print(self.currentToken)
        return word.replace('\n','')
        
    def previousToken(self):
        return self.tokenList[-2]

    def tokenType(self):
        return self.currentID

    def keyword(self):
        #return self.currentToken
        return self._keyword

    def symbol(self):
        return self.currentToken
        #return self._symbol

    def identifier(self):
        #return self.currentToken
        return self._identifier

    def intVal(self):
        #return self.currentToken
        return self._intVal

    def stringVal(self):
        #return self.currentToken[1:-1]
        return self._stringVal