# -*- coding: utf-8 -*-
from utils import parseQifDateTime


class Transaction(object):
    def __init__(self):
        self.account = None
        self.to_account = None
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

    @classmethod
    def parse(cls_, chunk):
        """
        """

        curItem = Transaction()
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
