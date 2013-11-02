# -*- coding: utf-8 -*-
from . import DEFAULT_DATETIME_FORMAT
from datetime import datetime


class Transaction(object):
    def __init__(self, date=None, amount=None, cleared=None, num=None,
                 payee=None, memo=None, address=None, category=None):
        self.to_account = None
        self.date_format = DEFAULT_DATETIME_FORMAT
        self.splits = []

        self.date = date and date or datetime.now()
        self.amount = amount
        self.cleared = cleared
        self.num = num
        self.payee = payee
        self.memo = memo
        self.address = address
        self.category = category

    def __repr__(self):
        return "<Transaction units=" + str(self.amount) + ">"

    def __str__(self):
        res = []
        res.append('D' + self.date.strftime(self.date_format))
        res.append('T%.2f' % self.amount)
        if self.cleared:
            res.append('C' + self.cleared)
        if self.payee:
            res.append('P' + self.payee)
        if self.memo:
            res.append('M' + self.memo)
        if self.address:
            res.append('A' + self.address)
        if self.to_account:
            res.append('L[%s]' % self.to_account)
        elif self.category:
            res.append('L' + self.category)
        for split in self.splits:
            res.append(str(split))
        res.append('^')
        return '\n'.join(res)


class AmountSplit(object):
    def __init__(self):
        self.category = None
        self.amount = None
        self.memo = None

        self.to_account = None

    def __str__(self):
        res = []
        if self.category:
            res.append('S' + self.category)
        else:
            res.append('S[%s]' % self.to_account)
        res.append('$%.2f' % self.amount)
        if self.memo:
            res.append('E' + self.memo)
        return '\n'.join(res)
