from .token import Token
from .token_type import TokenType


class Tokenizer:
    """
    Класс лексического анализатора. На вход принимает входную строку (текст) и
    на выходе выдает список токенов, описанных в классе TokenType. Также в файле tokens (grammar)
    есть соответствие между токеном и его лексемой.
    """
    code: str
    tokens: [Token]
    _NOT_SUPPORTED = '"\''

    def __init__(self, code=""):
        self.code = code
        self.tokens = []

    def read_from_file(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as fin:
            self.code = fin.read()

    def tokenize(self) -> list:
        buffer = ""

        for i, sym in enumerate(self.code):
            # есть список символов, которые не поддерживаются
            # в курсовой работе не поддерживаются строки и в списке
            # __NOT_SUPPORTED они описаны

            if sym in Tokenizer._NOT_SUPPORTED:
                raise ValueError(f"Symbol '{sym}' are not supported at this version")
            if self.is_sep(sym):
                # если символ - разделитель => передает обработчику
                buffer = self.sep_handler(buffer, sym)
            else:
                # иначе дальше заполняем буффер
                buffer += sym

        # если что-то осталось - внесем в список токенов
        if buffer != "":
            self.tokens.append(Token(buffer))

        # передаем управление методу, который 'соединяет' составные токены (допустим <=)
        self.tokens = self.adj_sub(self.tokens)
        return self.tokens

    def sep_handler(self, buffer, sym):
        if buffer != "":
            instance = Token(buffer)
            self.tokens.append(instance)
            buffer = ""
        # тут например обрабатываются +, -  и т.д, единичные символы
        if sym != " " and sym != '\n' and sym != '\t':
            instance = Token(sym)
            self.tokens.append(instance)
        return buffer

    def adj_sub(self, raw_tokens):
        hatch_tokens = []
        i = 0
        while i < len(raw_tokens):
            # проверка на соответствие
            if i < len(raw_tokens) - 1 and self.is_adj_operator(raw_tokens[i], raw_tokens[i + 1]):
                instance = Token(raw_tokens[i].lexeme + raw_tokens[i + 1].lexeme)
                hatch_tokens.append(instance)
                i += 2
            else:
                instance = Token(raw_tokens[i].lexeme)
                hatch_tokens.append(instance)
                i += 1

        return hatch_tokens

    @staticmethod
    def is_adj_operator(first: Token, second: Token) -> bool:
        return (first.lexeme in "<>=+-*/:!" and second.lexeme == "=") or \
               (first.lexeme == "+" and second.lexeme == "+") or \
               (first.lexeme == "-" and second.lexeme == "-") or \
               (first.lexeme == "/" and second.lexeme == "*") or \
               (first.lexeme == "*" and second.lexeme == "/") or \
               (first.lexeme == "&" and second.lexeme == "&") or \
               (first.lexeme == "|" and second.lexeme == "|")

    @staticmethod
    def is_sep(sym) -> bool:
        """
        возвращает True если sym - разделитель
        """
        return sym in " ()+-*/[]<>{}=!:;.,\n\t\r"
