import unittest
import os
from qifparse.qifparse import QIFParser

filename = os.path.join(os.path.dirname(__file__), u'file.qif')

class TestQIFParsing(unittest.TestCase):

    def testParseFile(self):
        qif = QIFParser.parse(open(filename))
        self.assertTrue(qif)


if __name__ == "__main__":
    import unittest
    unittest.main()
