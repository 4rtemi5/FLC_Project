from rply import LexerGenerator


class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        self.lexer.add('PRINT', r'print')
        self.lexer.add('MAIN', r'main')
        self.lexer.add('NUMBER', r'\d+(\.\d+)?')
        self.lexer.add('STRING', '(""".*?""")|(".*?")|(\'.*?\')')
        self.lexer.add('IF', r'if(?!\w)')
        self.lexer.add('ELSE', r'else(?!\w)')
        self.lexer.add('WHILE', r'while(?!\w)')
        self.lexer.add('LET', r'let(?!\w)')
        self.lexer.add('IDENTIFIER', r"[a-zA-Z_][a-zA-Z0-9_]*")
        self.lexer.add('==', r'==')
        self.lexer.add('!=', r'!=')
        self.lexer.add('>=', r'>=')
        self.lexer.add('<=', r'<=')
        self.lexer.add('>', r'>')
        self.lexer.add('<', r'<')
        self.lexer.add('=', r'=')
        self.lexer.add('{', r'\{')
        self.lexer.add('}', r'\}')
        self.lexer.add('|', r'\|')
        self.lexer.add('SEMICOLON', r';')
        self.lexer.add('SUM', r'\+')
        self.lexer.add('SUB', r'-')
        self.lexer.add('MUL', r'\*')
        self.lexer.add('DIV', r'/')
        self.lexer.add('(', r'\(')
        self.lexer.add(')', r'\)')
        self.lexer.add('NEWLINE', r'\n')

        # ignore whitespace
        self.lexer.ignore('[ \t\r\f\v]+')
        # self.lexer.ignore(r'[^\S\r\n]')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
