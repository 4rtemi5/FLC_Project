import warnings

from rply import ParserGenerator
from rply.errors import ParserGeneratorWarning

from ast import *

warnings.filterwarnings("ignore", category=ParserGeneratorWarning)


class Parser:
    def __init__(self, module, builder, printf):
        self.pg = ParserGenerator(
            # A list of all token names, accepted by the parser.
            ['STRING', 'NUMBER',
             'IDENTIFIER', 'BOOLEAN',
             'SUM', 'SUB', 'MUL', 'DIV',
             'IF', 'ELSE', 'LET', 'WHILE',
             '(', ')', '=', '==', '!=', '>=', '<=', '<', '>',
             '{', '}',
             'NEWLINE', 'PRINT',

             ],
            # A list of precedence rules with ascending precedence, to
            # disambiguate ambiguous production rules.
            precedence=[
                ('left', ['LET', ]),
                ('left', ['=']),
                ('left', ['[', ']', ',']),
                ('left', ['IF', 'ELSE', 'NEWLINE', 'WHILE', ]),
                ('left', ['==', '!=', '>=', '>', '<', '<=', ]),
                ('left', ['SUM', 'SUB', ]),
                ('left', ['MUL', 'DIV', ]),
                ('left', ['NEG', ]),

            ]
        )
        self.module = module
        self.builder = builder
        self.printf = printf

    def parse(self):

        @self.pg.production('main : statement_list')
        def parse_main(p):
            return MainFunction(self.builder, self.module, self.printf, p[0])

        @self.pg.production('statement_list : statement_list statement_list')
        def stmt_expr_arg_list(p):
            if not p[0]:
                return p[1]
            elif not p[1]:
                return p[0]
            else:
                return p[0] + p[1]

        @self.pg.production('statement_list : statement_list statement')
        def stmt_expr_arg_list(p):
            if p[1] is None:
                return p[0]
            return p[0] + [p[1]]

        @self.pg.production('statement_list : statement')
        def one_to_list(p):
            if p[0] is None:
                return []
            return [p[0]]

        #
        # @self.pg.production('statement_list : statement NEWLINE')
        # def single_to_list(p):
        #     if p[0] is None:
        #         return []
        #     return [p[0]]

        @self.pg.production('statement : NEWLINE')
        def newline_stmt(_):
            return None

        @self.pg.production('statement : PRINT ( expression )')
        def println(p):
            return Print(self.builder, self.module, self.printf, p[2])

        @self.pg.production('statement : LET IDENTIFIER = expression')
        def assign_var(p):
            name = p[1].value
            value = p[3]
            return VariableInstance(self.builder, self.module, self.printf, name, value)

        @self.pg.production('statement : IF ( expression ) block ')
        @self.pg.production('statement : IF ( expression ) block ELSE block')
        def if_cond(p):
            cond = p[2]
            if_block = p[4]
            if len(p) > 5:
                else_block = p[6]
                return IfElse(self.builder, self.module, cond, if_block, else_block)
            else:
                return IfElse(self.builder, self.module, cond, if_block)


        @self.pg.production('statement : WHILE ( expression ) block ')
        def if_cond(p):
            cond = p[2]
            if_block = p[4]
            return While(self.builder, self.module, cond, if_block)

        @self.pg.production('block : { statement_list }')
        def sblock(p):
            return p[1]

        @self.pg.production('block : { statement }')
        def sblock(p):
            return [p[1]]

        @self.pg.production('expression : IDENTIFIER')
        def read_var(p):
            name = p[0].value
            var = Variable(self.builder, self.module, self.printf, name)
            return var

        @self.pg.production('expression : expression <= expression')
        @self.pg.production('expression : expression < expression')
        @self.pg.production('expression : expression > expression')
        @self.pg.production('expression : expression >= expression')
        @self.pg.production('expression : expression != expression')
        @self.pg.production('expression : expression == expression')
        def compare(p):
            left = p[0]
            right = p[2]
            operation = p[1].gettokentype()
            return Comparison(self.builder, self.module, self.printf, left, right, operation)

        @self.pg.production('expression : expression MUL expression')
        @self.pg.production('expression : expression DIV expression')
        @self.pg.production('expression : expression SUM expression')
        @self.pg.production('expression : expression SUB expression')
        def expression(p):
            left = p[0]
            right = p[2]
            operator = p[1]
            if operator.gettokentype() == 'MUL':
                return Mul(self.builder, self.module, left, right)
            elif operator.gettokentype() == 'DIV':
                return Div(self.builder, self.module, left, right)
            elif operator.gettokentype() == 'SUM':
                return Sum(self.builder, self.module, left, right)
            elif operator.gettokentype() == 'SUB':
                return Sub(self.builder, self.module, left, right)

        @self.pg.production('expression : ( expression )')
        def paren_number(p):
            return p[1]

        @self.pg.production('expression : SUB expression', precedence='NEG')
        def signed_number(p):
            if p[0].gettokentype() == 'SUB':
                return Neg(self.builder, self.module, p[1])

        @self.pg.production('expression : NUMBER')
        def number(p):
            return Number(self.builder, self.module, self.printf, p[0])

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
