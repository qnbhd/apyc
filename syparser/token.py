import os
from typing import Dict, Tuple
from .exceptions.grammar_exception import GrammarException
from .token_type import TokenType

_GRAMMAR_FILE = os.path.join( os.path.dirname( __file__ ), '../grammar/tokens' )


def get_tokens_bijection_from_grammar_file(file: str) -> Dict[str, TokenType]:
    def _unpack(raw_) -> Tuple[str, str]:
        if len(raw_) == 2:
            token_name_, lexeme_ = raw_
            return token_name_, lexeme_
        elif len(raw_) == 1:
            token_name_, = raw_
            return token_name_, ''
        else:
            raise GrammarException('Invalid grammar line')

    tokens = {}

    with open(file, 'r') as file:
        for line in file:
            raw = [identifier.strip("'") for identifier in line.split()]
            if not raw:
                continue
            token_name, lexeme = _unpack(raw)
            tokens[lexeme] = TokenType[token_name]

    return tokens


class Token:
    __DEFINED_TOKENS_DICT = get_tokens_bijection_from_grammar_file(_GRAMMAR_FILE)

    def __init__(self, lexeme: str):
        self.lexeme = lexeme
        self.type = self.wto(self.lexeme)

    @staticmethod
    def wto(lexeme):
        if Token.is_number(lexeme):
            return TokenType.NUMBER
        return Token.__DEFINED_TOKENS_DICT.get(lexeme, TokenType.NAME)

    @staticmethod
    def is_number(lexeme: str) -> bool:
        if lexeme.find('.') != -1:
            raise ValueError("Decimal numbers is not supported for this version")
        return lexeme.isdigit()

    def __str__(self):
        return "(" + str(self.type) + ", " + self.lexeme + ")"

    def __repr__(self):
        return self.__str__()
