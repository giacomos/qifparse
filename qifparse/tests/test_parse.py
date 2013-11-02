# -*- coding: utf-8 -*-
import unittest
import os
from qifparse.parser import QifParser

filename = os.path.join(os.path.dirname(__file__), 'file.qif')


class TestQIFParsing(unittest.TestCase):

    def testParseFile(self):
        qif = QifParser.parse(open(filename))
        self.assertTrue(qif)

    def testWriteFile(self):
        data = open(filename).read()
        qif = QifParser.parse(open(filename))
        self.assertEquals(data, str(qif))


if __name__ == "__main__":
    import unittest
    unittest.main()
