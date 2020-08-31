import unittest
from syparser.tokenizer import Tokenizer
from syparser.token_type import TokenType


class MyTestCase(unittest.TestCase):
    def test_base_tokens(self):
        case = "5 - 6 / 7 * 10 <= 77 [] >> !="
        result = Tokenizer(case).tokenize()
        good = [TokenType.NUMBER, TokenType.MINUS, TokenType.NUMBER,
                TokenType.SLASH, TokenType.NUMBER, TokenType.STAR, TokenType.NUMBER,
                TokenType.LESSEQUAL, TokenType.NUMBER, TokenType.LSQB,
                TokenType.RSQB, TokenType.GREATER, TokenType.GREATER,
                TokenType.NOTEQUAL]

        for tok, good_tok in zip(result, good):
            with self.subTest(case=good_tok):
                self.assertEqual(tok.type, good_tok)

    def test_identifiers_for_tokens(self):
        case = """
        int a = 5;

        for (int i = 0; i < 10; i = i + 1) {
            printf(i);
        }
        """
        good = [TokenType.TYPEINT, TokenType.NAME, TokenType.EQUAL,
                TokenType.NUMBER, TokenType.SEMI, TokenType.FOR,
                TokenType.LPAR, TokenType.TYPEINT, TokenType.NAME,
                TokenType.EQUAL, TokenType.NUMBER, TokenType.SEMI,
                TokenType.NAME, TokenType.LESS, TokenType.NUMBER,
                TokenType.SEMI, TokenType.NAME, TokenType.EQUAL,
                TokenType.NAME, TokenType.PLUS, TokenType.NUMBER,
                TokenType.RPAR, TokenType.LBRACE, TokenType.PRINTF,
                TokenType.LPAR, TokenType.NAME, TokenType.RPAR,
                TokenType.SEMI, TokenType.RBRACE
                ]

        result = Tokenizer(case).tokenize()

        for tok, good_tok in zip(result, good):
            with self.subTest(case=good_tok):
                self.assertEqual(tok.type, good_tok)

    def test_if_statement(self):
        case = """
        if (a <= 6) {
            printf(10);
        }
        """
        good = [TokenType.IF, TokenType.LPAR, TokenType.NAME,
                TokenType.LESSEQUAL, TokenType.NUMBER, TokenType.RPAR,
                TokenType.LBRACE, TokenType.PRINTF, TokenType.LPAR,
                TokenType.NUMBER, TokenType.RPAR, TokenType.SEMI]

        result = Tokenizer(case).tokenize()

        for tok, good_tok in zip(result, good):
            with self.subTest(case=good_tok):
                self.assertEqual(tok.type, good_tok)


if __name__ == '__main__':
    unittest.main()
