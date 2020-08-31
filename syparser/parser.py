from .tokenizer import Tokenizer
from .token_type import TokenType
from .token import Token

from .ast import AST
from .ast_node import AstNode
from .ast_node_type import AstNodeType


class Parser:
    tokenizer: Tokenizer
    ast: AST

    tokens: list
    pos: int

    tokens_count: int

    def __init__(self, file_path):
        self.lexer = Tokenizer()
        self.lexer.read_from_file(file_path)
        self.ast = AST()
        self.tokens = self.lexer.tokenize()  # список токенов!
        self.pos = 0

        # self.lexer.print()
        # self.lexer.log_out()

        self.tokens_count = len(self.tokens)
        # self.packages_map = Packages()

        self.in_block_not_main = False

    def get(self, relative_position: int) -> Token:
        position = self.pos + relative_position
        if position >= self.tokens_count:
            return Token('\0')
        return self.tokens[position]

    def match(self, type_: TokenType) -> bool:
        current = self.get(0)

        if type_ != current.type:
            return False

        self.pos += 1
        return True

    def consume(self, type_: TokenType) -> Token:
        current = self.get(0)

        if type_ != current.type:
            raise RuntimeError("Token " + str(current) + " doesn't match " + str(type_))

        self.pos += 1
        return current

    def parse(self):
        self.ast.tree = AstNode(AstNodeType.PROGRAM)

        self.consume(TokenType.TYPEINT)
        self.consume(TokenType.NAME)

        self.consume(TokenType.LPAR)
        self.consume(TokenType.RPAR)

        statement = self.bracket_expression()

        # statement_list_package_node: AstNode = AstNode(AstNodeType.STATEMENT_LIST, '', package_node)
        statement_list_node: AstNode = AstNode(AstNodeType.STATEMENT_LIST, '', statement)

        self.ast.tree.op1 = statement_list_node
        self.ast.print()
        self.ast.log_out()
        self.ast.variables.print()
        self.ast.variables.log_out()

    def bracket_expression(self) -> AstNode:

        self.consume(TokenType.LBRACE)

        node = None

        while not self.match(TokenType.RBRACE):
            statement_node = self.statement()
            node = AstNode(AstNodeType.STATEMENT_LIST, '', node, statement_node)

        return node

    def program(self) -> AstNode:
        node = None

        while not self.match(TokenType.EOF):
            statement_node = self.statement()
            node = AstNode(AstNodeType.STATEMENT_LIST, '', node, statement_node)

        return node

    def statement(self) -> AstNode:
        if self.match(TokenType.IF):
            return self.if_else_block()

        if self.match(TokenType.FOR):
            return self.for_block()

        if self.get(0).lexeme == 'printf':
            return self.print_operator()

        return self.expression_statement()

    def print_operator(self):
        self.consume(TokenType.PRINTF)
        self.consume(TokenType.LPAR)
        arg_node: AstNode = self.expression()
        self.consume(TokenType.RPAR)

        return AstNode(AstNodeType.PRINT, '', arg_node)

    def if_else_block(self) -> AstNode:

        condition = self.par_expression()

        node_type = AstNodeType.IF

        if_block_statement = self.bracket_expression()

        else_block = None
        if self.match(TokenType.ELSE):
            node_type = AstNodeType.IF_ELSE
            self.match(TokenType.ELSE)
            else_block = self.bracket_expression()

        return AstNode(node_type, '', condition, if_block_statement, else_block)

    def for_block(self) -> AstNode:
        self.consume(TokenType.LPAR)
        initialization_node: AstNode = self.expression()
        self.consume(TokenType.SEMI)

        condition_node: AstNode = self.expression()
        self.consume(TokenType.SEMI)

        aftereffect_node: AstNode = self.expression()
        self.consume(TokenType.RPAR)

        statement_node: AstNode = self.bracket_expression()

        return AstNode(AstNodeType.FOR, '', initialization_node, condition_node, aftereffect_node, statement_node)

    def declaration_statement(self) -> AstNode:
        self.consume(TokenType.TYPEINT)

        current: Token = self.get(0)

        self.consume(TokenType.NAME)
        variable_name: str = current.lexeme
        self.consume(TokenType.EQUAL)

        self.ast.variables.add(variable_name)

        expression_node: AstNode = self.expression()

        variable_declaration_node: AstNode = AstNode(AstNodeType.VARIABLE_DECLARATION, variable_name)

        return AstNode(AstNodeType.SET, '', variable_declaration_node, expression_node)

    def expression_statement(self) -> AstNode:

        node = self.expression()

        self.match(TokenType.SEMI)

        return node

    def expression(self) -> AstNode:
        return self.assignment_expression()

    def assignment_expression(self) -> AstNode:
        node: AstNode = self.logical_or()

        if self.match(TokenType.EQUAL):
            assignment_expression_node: AstNode = self.assignment_expression()

            return AstNode(AstNodeType.SET, '', node, assignment_expression_node)

        return node

    def logical_or(self) -> AstNode:
        node: AstNode = self.logical_and()

        if self.match(TokenType.DOUBLEVBAR):
            return AstNode(AstNodeType.OR, '', node, self.logical_or())

        return node

    def logical_and(self) -> AstNode:
        node: AstNode = self.equality()

        if self.match(TokenType.DOUBLEAMPER):
            return AstNode(AstNodeType.AND, '', node, self.logical_and())

        return node

    def equality(self) -> AstNode:
        result: AstNode = self.conditional()

        if self.match(TokenType.EQEQUAL):
            return AstNode(AstNodeType.EQUAL, '', result, self.conditional())

        if self.match(TokenType.NOTEQUAL):
            return AstNode(AstNodeType.NOT_EQUAL, '', result, self.conditional())

        return result

    def conditional(self) -> AstNode:
        result: AstNode = self.add()

        if self.match(TokenType.LESS):
            return AstNode(AstNodeType.LESS, '', result, self.add())

        if self.match(TokenType.GREATER):
            return AstNode(AstNodeType.GREATER, '', result, self.add())

        if self.match(TokenType.LESSEQUAL):
            return AstNode(AstNodeType.LESS_OR_EQUAL, '', result, self.add())

        if self.match(TokenType.GREATEREQUAL):
            return AstNode(AstNodeType.GREATER_EQUAL, '', result, self.add())

        return result

    def add(self) -> AstNode:
        multy_node: AstNode = self.multy()

        if self.match(TokenType.PLUS):
            temp_node = self.add()
            return AstNode(AstNodeType.ADD, '', multy_node, temp_node)

        if self.match(TokenType.MINUS):
            temp_node = self.add()
            return AstNode(AstNodeType.SUB, '', multy_node, temp_node)

        return multy_node

    def multy(self) -> AstNode:
        unary_node: AstNode = self.unary()

        if self.match(TokenType.STAR):
            temp_node = self.multy()
            return AstNode(AstNodeType.MUL, '', unary_node, temp_node)

        if self.match(TokenType.SLASH):
            temp_node = self.multy()
            return AstNode(AstNodeType.DIV, '', unary_node, temp_node)

        return unary_node

    def unary(self) -> AstNode:
        if self.match(TokenType.MINUS):
            temp_node: AstNode = self.primary()
            return AstNode(AstNodeType.UNARY_MINUS, '', temp_node)

        return self.primary()

    def primary(self) -> AstNode:
        current: Token = self.get(0)

        if self.match(TokenType.NUMBER):
            number_node: AstNode = AstNode(AstNodeType.INTEGER_CONST, current.lexeme)
            return number_node

        if current.type == TokenType.TYPEINT and self.get(1).type == TokenType.NAME:
            return self.declaration_statement()

        if self.match(TokenType.NAME):
            identifier: str = current.lexeme

            if self.ast.variables.contains(identifier):
                return AstNode(AstNodeType.USING_VARIABLE, identifier)

        if current.type == TokenType.LPAR:
            return self.par_expression()

        return None

    def par_expression(self) -> AstNode:
        if not self.match(TokenType.LPAR):
            raise Exception("LEFT PAREN WAS EXCEPTED")

        expr_node: AstNode = self.expression()

        if not self.match(TokenType.RPAR):
            raise Exception("RIGHT PAREN WAS EXCEPTED")

        return expr_node
