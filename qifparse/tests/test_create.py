# -*- coding: utf-8 -*-
import unittest
from qifparse import qif


class TestCreateQIF(unittest.TestCase):

    def testcreateQifFile(self):
        qif_obj = qif.Qif()
        acc = qif.Account(name='My Cc', account_type='Bank')
        qif_obj.add_account(acc)
        cat = qif.Category(name='food')
        qif_obj.add_category(cat)
        tr1 = qif.Transaction(amount=0.55)
        acc.add_transaction(tr1, header='!Type:Bank')

        tr2 = qif.Transaction()
        tr2.amount = -6.55
        tr2.to_account = 'Cash'
        acc.add_transaction(tr2)
        self.assertTrue(str(qif_obj))

    def testAddandGetAccounts(self):
        qif_obj = qif.Qif()
        acc = qif.Account(name='My Cc')
        qif_obj.add_account(acc)
        res = qif_obj.get_accounts(name='My Cc')
        self.failUnless(len(res))

    def testAddandGetCategories(self):
        qif_obj = qif.Qif()
        cat = qif.Category(name='my cat')
        qif_obj.add_category(cat)
        res = qif_obj.get_categories(name='my cat')
        self.failUnless(len(res))


if __name__ == "__main__":
    import unittest
    unittest.main()
