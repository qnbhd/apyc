from enum import Enum, auto


class TokenType(Enum):
    """
    Класс перечисление со списком зарезерврованных токенов
    """
    ENDMARKER = auto(),
    NAME = auto(),
    NUMBER = auto(),
    LPAR = auto(),
    RPAR = auto(),
    LSQB = auto(),
    RSQB = auto(),
    COLON = auto(),
    COMMA = auto(),
    SEMI = auto(),
    PLUS = auto(),
    MINUS = auto(),
    STAR = auto(),
    SLASH = auto(),
    VBAR = auto(),
    DOUBLEVBAR = auto(),
    DOUBLEAMPER = auto(),
    AMPER = auto(),
    LESS = auto(),
    GREATER = auto(),
    EQUAL = auto(),
    DOT = auto(),
    PERCENT = auto(),
    LBRACE = auto(),
    RBRACE = auto(),
    EQEQUAL = auto(),
    NOTEQUAL = auto(),
    LESSEQUAL = auto(),
    GREATEREQUAL = auto(),
    TILDE = auto(),
    CIRCUMFLEX = auto(),
    LEFTSHIFT = auto(),
    RIGHTSHIFT = auto(),
    DOUBLESTAR = auto(),
    PLUSEQUAL = auto(),
    MINEQUAL = auto(),
    STAREQUAL = auto(),
    SLASHEQUAL = auto(),
    PERCENTEQUAL = auto(),
    AMPEREQUAL = auto(),
    VBAREQUAL = auto(),
    CIRCUMFLEXEQUAL = auto(),
    LEFTSHIFTEQUAL = auto(),
    RIGHTSHIFTEQUAL = auto(),
    DOUBLESTAREQUAL = auto(),
    DOUBLESLASH = auto(),
    DOUBLESLASHEQUAL = auto(),
    AT = auto(),
    ATEQUAL = auto(),
    RARROW = auto(),
    ELLIPSIS = auto(),
    COLONEQUAL = auto(),
    FOR = auto(),
    IF = auto(),
    ELSE = auto()
    TYPEINT = auto()
    PRINTF = auto()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name
