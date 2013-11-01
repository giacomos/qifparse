# -*- coding: utf-8 -*-


class Category(object):

    def __init__(self):
        self.name = None  # N
        self.description = None  # D
        self.tax_related = None  # T, not tax related if omitted
        self.income_category = None  # I
        self.expense_category = True  # E
        self.budget_amount = None  # B
        self.tax_schedule_info = None  # R

    def __repr__(self):
        return '<Category: %s>' % self.name

    def __str__(self):
        res = []
        res.append('N' + self.name)
        if self.description:
            res.append('D' + self.description)
        if self.tax_related:
            res.append('T' + self.tax_related)
        if self.income_category:
            res.append('I')
        else:
            res.append('E')
        if self.budget_amount:
            res.append('B' + self.budget_amount)
        if self.tax_schedule_info:
            res.append('R' + self.tax_schedule_info)
        res.append('^')
        return '\n'.join(res)

    @classmethod
    def parse(cls_, chunk):
        """
        """
        curItem = Category()
        lines = chunk.split('\n')
        for line in lines:
            if not len(line) or line[0] == '\n' or line.startswith('!Type'):
                continue
            elif line[0] == 'E':
                curItem.expense_category = True
            elif line[0] == 'I':
                curItem.income_category = True
                curItem.expense_category = False  # if ommitted is True
            elif line[0] == 'T':
                curItem.tax_related = True
            elif line[0] == 'D':
                curItem.description = line[1:]
            elif line[0] == 'B':
                curItem.budget_amount = line[1:]
            elif line[0] == 'R':
                curItem.tax_schedule_info = line[1:]
            elif line[0] == 'N':
                curItem.name = line[1:]
        return curItem
