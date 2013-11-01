import sys
sys.path.append('..')
from unittest import TestCase
from qifparse import account
from qifparse import transaction
from qifparse import investment
from qifparse import category
from qifparse.qifparse import QIFParser

class TestQIFParsing(TestCase):

    def testSuccess(self):
        qif = QIFParser.parse(open_file('file.qif'), True)
        self.assertTrue(qif)


if __name__ == "__main__":
    import unittest
    unittest.main()
