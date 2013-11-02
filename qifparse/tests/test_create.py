# -*- coding: utf-8 -*-
import unittest
from qifparse import qif


class TestCreateQIF(unittest.TestCase):

    def testcreateQifFile(self):
        qif_obj = qif.Qif()
        acc = qif.Account()
        acc.name = 'My Cc'
        acc.account_type = 'Bank'
        qif_obj.add(acc)
        cat = qif.Category()
        cat.name = 'food'
        qif_obj.add(cat)
        tr1 = qif.Transaction()
        tr1.amount = 0.55
        acc.add(tr1)

        tr2 = qif.Transaction()
        tr2.amount = -6.55
        tr2.to_account = 'Cash'
        acc.add(tr2)
        self.assertTrue(str(qif_obj))


if __name__ == "__main__":
    import unittest
    unittest.main()
