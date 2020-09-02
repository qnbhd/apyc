from syparser.token import Token
from syparser.tokenizer import Tokenizer
from syparser.parser import Parser
from codegen.codegen import CodeGen

if __name__ == '__main__':
    parser = Parser('ex1.c')
    parser.parse()
    Ast = parser.ast
    # Ast.print()
    gk = CodeGen('ex1.asm', Ast)
    gk.generate()