# -*- coding: utf-8 -*-
from qifparse import account
from qifparse.transaction import Transaction
from qifparse import investment
from qifparse import category

NON_INVST_ACCOUNT_TYPES = [
    '!Type:Cash',
    '!Type:Bank',
    '!Type:Ccard',
    '!Type:Oth A',
    '!Type:Oth L',
    '!Type:Invoice',  # Quicken for business only
]


class QIF(object):
    def __init__(self, accounts=None, transactions=None,
                 categories=None, investments=None):
        self.accounts = accounts
        self.transactions = transactions
        self.categories = categories
        self.investments = investments

    def toString(self):
        res = []
        res.append('!Type:Cat')
        for cat in self.categories:
            res.append(str(cat))
        for acc in self.accounts:
            res.append(str(acc))
        return '\n'.join(res)


class QifParserException(Exception):
    pass


class QIFParser(object):

    def parseQIFdata(self, data):
        if len(data) == 0:
            raise QifParserException('Data is empty')
        res = {
            'accounts': [],
            'transactions': [],
            'categories': [],
            'investments': []
        }
        chunks = data.split('\n^\n')
        last_type = None
        parsers = {
            'categories': category.parseCategory,
            'accounts': account.parseAccount,
            'transactions': Transaction.parse,
            'investments': investment.parseInvestment
        }
        for chunk in chunks:
            if chunk.startswith('!Type:Cat'):
                last_type = 'categories'
            elif chunk.startswith('!Account'):
                last_type = 'accounts'
            elif chunk.split('\n')[0] in NON_INVST_ACCOUNT_TYPES:
                last_type = 'transactions'
            elif chunk.startswith('!Type:Invst'):
                last_type = 'investments'
                # TODO: I should check if the previous accout
                # is actually and investment account
            elif chunk.startswith('!Type:Class'):
                continue  # yet to be done!
            elif chunk.startswith('!Type:Memorized'):
                continue  # yet to be done!
            elif chunk.startswith('!'):
                raise QifParserException('Header not reconized')
            # if no header is recognized then
            # we use the previous one
            parsed_item = parsers[last_type](chunk)
            if last_type == 'transactions':
                parsed_item.account = res['accounts'][-1].name
            res[last_type].append(parsed_item)
        res = QIF(**res)
        return res
