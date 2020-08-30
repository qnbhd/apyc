import unittest
from syparser.token import Token
from syparser.token_type import TokenType


class TokenTypeTestCase(unittest.TestCase):
    def test_number(self):
        cases = ['1', '90', '34342']
        for b in cases:
            with self.subTest(case=b):
                tok = Token(b)
                self.assertEqual(tok.type, TokenType.NUMBER)

    def test_doubled_tokens(self):
        cases = ['==', '!=']
        good = [TokenType.EQEQUAL, TokenType.NOTEQUAL]

        for case, good_answer in zip(cases, good):
            with self.subTest(case=case):
                tok = Token(case)
                self.assertEqual(tok.type, good_answer)

    def test_raises(self):
        self.assertRaises(ValueError, Token.wto, '5.67')

    def test_name(self):
        tk = Token('abc')
        self.assertEqual(tk.type, TokenType.NAME)


if __name__ == '__main__':
    unittest.main()
