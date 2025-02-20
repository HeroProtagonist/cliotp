import unittest

from src.totp import Totp


# Expected values from Appendix B
class TotpTestCase(unittest.TestCase):
    def setUp(self):
        self.totp = Totp("12345678901234567890")

    def test_it(self):
        code = self.totp.generate_code(1111111109)
        print(code)
