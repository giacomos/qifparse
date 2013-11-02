# -*- coding: utf-8 -*-
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
