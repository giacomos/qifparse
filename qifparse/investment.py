# -*- coding: utf-8 -*-
from utils import parseQifDateTime


class Investment(object):
    def __init__(self):
        self.account = None
        self.to_account = None  # L, account for a trasnfer

        self.date = None  # D, date
        self.action = None  # N, investment action
        self.security = None  # Y, security name
        self.price = None  # I, price
        self.quantity = None  # Q, quantity
        self.cleared = None  # C, cleared status
        self.amount = None  # T, amount
        self.memo = None  # M, memo
        self.first_line = None  # P, text in the first line
        self.amount_transfer = None  # $, amount for a transfer
        self.commission = None  # O, commission_cost

    def __repr__(self):
        return "<Investment units=" + str(self.amount) + ">"

    @classmethod
    def parse(cls_, chunk):
        """
        """

        curItem = Investment()
        lines = chunk.split('\n')
        for line in lines:
            if not len(line) or line[0] == '\n' or line.startswith('!Type'):
                continue
            elif line[0] == 'D':
                curItem.date = parseQifDateTime(line[1:])
            elif line[0] == 'T':
                curItem.amount = float(line[1:])
            elif line[0] == 'N':
                curItem.action = line[1:]
            elif line[0] == 'Y':
                curItem.security = line[1:]
            elif line[0] == 'I':
                curItem.price = line[1:]
            elif line[0] == 'Q':
                curItem.quantity = line[1:]
            elif line[0] == 'C':
                curItem.cleared = line[1:]
            elif line[0] == 'M':
                curItem.memo = line[1:]
            elif line[0] == 'P':
                curItem.first_line = line[1:]
            elif line[0] == 'L':
                curItem.to_account = line[2:-1]
            elif line[0] == '$':
                curItem.amount_transfer = float(line[1:])
            elif line[0] == 'O':
                curItem.commission = float(line[1:])
        return curItem
