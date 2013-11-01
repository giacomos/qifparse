# -*- coding: utf-8 -*-
from qifparse.utils import parseQifDateTime
from . import DEFAULT_DATETIME_FORMAT


class Transaction(object):
    def __init__(self):
#        self.account = None
        self.to_account = None
        self.date_format = DEFAULT_DATETIME_FORMAT
        self.splits = []

        self.date = None
        self.amount = None
        self.cleared = None
        self.num = None
        self.payee = None
        self.memo = None
        self.address = None
        self.category = None
#        self.categoryInSplit = None
#        self.memoInSplit = None
#        self.amountOfSplit = None

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

    @classmethod
    def parse(cls_, chunk, date_format=None):
        """
        """

        curItem = Transaction()
        if date_format:
            curItem.date_format = date_format
        lines = chunk.split('\n')
        for line in lines:
            if not len(line) or line[0] == '\n' or line.startswith('!Type'):
                continue
            elif line[0] == 'D':
                curItem.date = parseQifDateTime(line[1:])
            elif line[0] == 'T':
                curItem.amount = float(line[1:])
            elif line[0] == 'C':
                curItem.cleared = line[1:]
            elif line[0] == 'P':
                curItem.payee = line[1:]
            elif line[0] == 'M':
                curItem.memo = line[1:]
            elif line[0] == 'A':
                curItem.address = line[1:]
            elif line[0] == 'L':
                cat = line[1:]
                if cat.startswith('['):
                    curItem.to_account = cat[1:-1]
                else:
                    curItem.category = cat
            elif line[0] == 'S':
                curItem.splits.append(AmountSplit())
                split = curItem.splits[-1]
                cat = line[1:]
                if cat.startswith('['):
                    split.to_account = cat[1:-1]
                else:
                    split.category = cat
            elif line[0] == 'E':
                split = curItem.splits[-1]
                split.memo = line[1:-1]
            elif line[0] == '$':
                split = curItem.splits[-1]
                split.amount = float(line[1:-1])
            else:
                # don't recognise this line; ignore it
                print ("Skipping unknown line:\n" + str(line))
        return curItem


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
