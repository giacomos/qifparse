# -*- coding: utf-8 -*-
import six
from qifparse.transaction import Transaction
from qifparse.investment import Investment

ACCOUNT_TYPES = [
    'Cash',
    'Bank',
    'Ccard',
    'Oth A',
    'Oth L',
    'Invoice',  # Quicken for business only
    'Invst',
]


class Account(object):

    def __init__(self, name=None, type=None, description=None,
                 credit_limit=None, balance_date=None, balance_amount=None):
        self.name = name  # N
        self.description = description  # D
        self.account_type = type  # T
        self.credit_limit = credit_limit  # L
        self.balance_date = balance_date  # /
        self.balance_amount = balance_amount  # $
        self._transactions = []

    def add(self, item):
        if not isinstance(item, Transaction) and \
           not isinstance(item, Investment):
            raise RuntimeError(
                six.u("item is not a Transaction or an Investment"))
        self._transactions.append(item)

    def set_type(self, type):
        if type and type not in ACCOUNT_TYPES:
            raise RuntimeError(
                six.u("%s is not a valid account type" % type))
        self._type = type

    def get_type(self):
        return self._type

    account_type = property(get_type, set_type)

    def __repr__(self):
        return '<Account: %s>' % self.name

    def __str__(self):
        res = []
        res.append('!Account')
        res.append('N' + self.name)
        if self.description:
            res.append('D' + self.description)
        res.append('T' + self.account_type)
        if self.credit_limit:
            res.append('L' + self.credit_limit)
        if self.balance_date:
            res.append('/' + self.balance_date)
        if self.balance_amount:
            res.append('$' + self.balance_amount)
        res.append('^')
        if self._transactions:
            res.append('!Type:%s' % self.account_type)
            for tr in self._transactions:
                res.append(str(tr))
        return '\n'.join(res)
