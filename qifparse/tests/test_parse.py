# -*- coding: utf-8 -*-
import unittest
import os
from qifparse.parser import QifParser

filename = os.path.join(os.path.dirname(__file__), 'file.qif')
filename2 = os.path.join(os.path.dirname(__file__), 'transactions_only.qif')


class TestQIFParsing(unittest.TestCase):

    def testParseFile(self):
        qif = QifParser.parse(open(filename))
        self.assertTrue(qif)

    def testWriteFile(self):
        data = open(filename).read()
        qif = QifParser.parse(open(filename))
#        out = open('out.qif', 'w')
#        out.write(str(qif))
#        out.close()
        self.assertEquals(data, str(qif))

    def testParseTransactionsFile(self):
        data = open(filename2).read()
        qif = QifParser.parse(open(filename2))
#        out = open('out.qif', 'w')
#        out.write(str(qif))
#        out.close()
        self.assertEquals(data, str(qif))

if __name__ == "__main__":
    import unittest
    unittest.main()
