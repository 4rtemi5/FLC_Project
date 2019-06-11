from codegen import CodeGen
from lexer import Lexer
from parser import Parser

fname = "input.flc"

print('\nCompiling "%s" zo IR...' % fname)

with open(fname) as f:
    text_input = f.read().strip()

lexer = Lexer().get_lexer()
tokens = lexer.lex(text_input)

codegen = CodeGen()

module = codegen.module
builder = codegen.builder
printf = codegen.printf

pg = Parser(module, builder, printf)
pg.parse()
parser = pg.get_parser()

# print(list(tokens))

parser.parse(tokens).eval()

codegen.create_ir()
codegen.save_ir('output.ll')

print('Done. LLVM IR written to "output.ll"')
