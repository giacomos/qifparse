# -*- coding: utf-8 -*-
from qifparse.utils import parseQifDateTime
from . import DEFAULT_DATETIME_FORMAT


class Investment(object):
    def __init__(self):
        self.account = None
        self.to_account = None  # L, account for a trasnfer
        self.date_format = DEFAULT_DATETIME_FORMAT

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

    def __str__(self):
        res = []
        res.append('D' + self.date.strftime(self.date_format))
        if self.action:
            res.append('N' + self.action)
        if self.security:
            res.append('Y' + self.security)
        if self.price:
            res.append('I%.3f' % self.price)
        if self.quantity:
            res.append('Q' + self.quantity)
        if self.cleared:
            res.append('C' + self.cleared)
        if self.amount:
            res.append('T%.2f' % self.amount)
        if self.memo:
            res.append('M' + self.memo)
        if self.first_line:
            res.append('P' + self.first_line)
        if self.to_account:
            res.append('L[%s]' % self.to_account)
            res.append('$%.2f' % self.amount_transfer)
        if self.commission:
            res.append('O' + self.commission)
        res.append('^')
        return '\n'.join(res)

    @classmethod
    def parse(cls_, chunk, date_format=None):
        """
        """

        curItem = Investment()
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
            elif line[0] == 'N':
                curItem.action = line[1:]
            elif line[0] == 'Y':
                curItem.security = line[1:]
            elif line[0] == 'I':
                curItem.price = float(line[1:])
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
