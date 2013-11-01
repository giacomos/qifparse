# -*- coding: utf-8 -*-
import six
from qifparse.transaction import Transaction
from qifparse.account import Account
from qifparse.investment import Investment
from qifparse.category import Category
from . import DEFAULT_DATETIME_FORMAT

NON_INVST_ACCOUNT_TYPES = [
    '!Type:Cash',
    '!Type:Bank',
    '!Type:Ccard',
    '!Type:Oth A',
    '!Type:Oth L',
    '!Type:Invoice',  # Quicken for business only
]


class Qif(object):
    def __init__(self, accounts=None, transactions=None,
                 categories=None, investments=None):
        self.accounts = accounts
        self.transactions = transactions
        self.categories = categories
        self.investments = investments

    def __str__(self):
        res = []
        res.append('!Type:Cat')
        for cat in self.categories:
            res.append(str(cat))
        for acc in self.accounts:
            res.append(str(acc))
            if acc.name in self.transactions:
                res.append('!Type:%s' % acc.account_type)
                for tr in self.transactions[acc.name]:
                    res.append(str(tr))
            if acc.name in self.investments:
                res.append('!Type:%s' % acc.account_type)
                for tr in self.investments[acc.name]:
                    res.append(str(tr))
        res.append('')
        return '\n'.join(res)


class QifParserException(Exception):
    pass


class QifParser(object):

    @classmethod
    def parse(cls_, file_handle, date_format=None):
        if isinstance(file_handle, type('')):
            raise RuntimeError(
                six.u("parse() takes in a file handle, not a string"))
        data = file_handle.read()
        if len(data) == 0:
            raise QifParserException('Data is empty')
        res = {
            'accounts': [],
            'categories': [],
            'transactions': {},
            'investments': {}
        }
        chunks = data.split('\n^\n')
        last_type = None
        parsers = {
            'categories': Category.parse,
            'accounts': Account.parse,
            'transactions': Transaction.parse,
            'investments': Investment.parse
        }
        for chunk in chunks:
            if not chunk:
                continue
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
            if last_type == 'transactions' or last_type == 'investments':
                parsed_item = parsers[last_type](chunk, date_format)
                account = res['accounts'][-1].name
                if not account in res[last_type]:
                    res[last_type][account] = []
                res[last_type][account].append(parsed_item)
            else:
                parsed_item = parsers[last_type](chunk)
                res[last_type].append(parsed_item)
        res = Qif(**res)
        return res
