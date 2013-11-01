# -*- coding: utf-8 -*-
from qifparse.utils import parseQifDateTime


class Account(object):

    def __init__(self):
        self.name = None  # N
        self.description = None  # D
        self.account_type = None  # T
        self.credit_limit = None  # L
        self.balance_date = None  # /
        self.balance_amount = None  # $

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
        return '\n'.join(res)

    @classmethod
    def parse(cls_, chunk):
        """
        """
        curItem = Account()
        lines = chunk.split('\n')
        for line in lines:
            if not len(line) or line[0] == '\n' or line.startswith('!Account'):
                continue
            elif line[0] == 'N':
                curItem.name = line[1:]
            elif line[0] == 'D':
                curItem.description = line[1:]
            elif line[0] == 'T':
                curItem.account_type = line[1:]
            elif line[0] == 'L':
                curItem.credit_limit = line[1:]
            elif line[0] == '/':
                curItem.balance_date = parseQifDateTime(line[1:])
            elif line[0] == '$':
                curItem.balance_amount = line[1:]
            else:
                print('Line not recognized: ' + line)
        return curItem
