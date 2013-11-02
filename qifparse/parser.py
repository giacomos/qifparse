# -*- coding: utf-8 -*-
import six
from datetime import datetime
from qifparse.transaction import Transaction
from qifparse.transaction import AmountSplit
from qifparse.account import Account
from qifparse.investment import Investment
from qifparse.category import Category
from qifparse.qif import Qif
from . import DEFAULT_DATETIME_FORMAT

NON_INVST_ACCOUNT_TYPES = [
    '!Type:Cash',
    '!Type:Bank',
    '!Type:Ccard',
    '!Type:Oth A',
    '!Type:Oth L',
    '!Type:Invoice',  # Quicken for business only
]


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
        qif_obj = Qif()
        chunks = data.split('\n^\n')
        last_type = None
        last_account = None
        parsers = {
            'categories': Category.parse,
            'accounts': cls_.parseAccount,
            'transactions': cls_.parseTransaction,
            'investments': cls_.parseInvestment
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
            if last_type in ['categories', 'accounts']:
                parsed_item = parsers[last_type](chunk)
                if last_type == 'accounts':
                    last_account = parsed_item
                qif_obj.add(parsed_item)
            else:
                parsed_item = parsers[last_type](chunk, date_format)
                last_account.add(parsed_item)
        return qif_obj

    @classmethod
    def parseAccount(cls_, chunk):
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
                curItem.balance_date = cls_.parseQifDateTime(line[1:])
            elif line[0] == '$':
                curItem.balance_amount = line[1:]
            else:
                print('Line not recognized: ' + line)
        return curItem

    @classmethod
    def parseTransaction(cls_, chunk, date_format=None):
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
                curItem.date = cls_.parseQifDateTime(line[1:])
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

    @classmethod
    def parseInvestment(cls_, chunk, date_format=None):
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
                curItem.date = cls_.parseQifDateTime(line[1:])
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

    @classmethod
    def parseQifDateTime(cls_, qdate):
        """ convert from QIF time format to ISO date string

        QIF is like "7/ 9/98"  "9/ 7/99" or "10/10/99" or "10/10'01" for y2k
             or, it seems (citibankdownload 20002) like "01/22/2002"
             or, (Paypal 2011) like "3/2/2011".
        ISO is like   YYYY-MM-DD  I think @@check
        """
        if qdate[1] == "/":
            qdate = "0" + qdate   # Extend month to 2 digits
        if qdate[4] == "/":
            qdate = qdate[:3]+"0" + qdate[3:]   # Extend month to 2 digits
        for i in range(len(qdate)):
            if qdate[i] == " ":
                qdate = qdate[:i] + "0" + qdate[i+1:]
        if len(qdate) == 10:  # new form with YYYY date
            iso_date = qdate[6:10] + "-" + qdate[3:5] + "-" + qdate[0:2]
            return datetime.strptime(iso_date, '%Y-%m-%d')
        if qdate[5] == "'":
            C = "20"
        else:
            C = "19"
        iso_date = C + qdate[6:8] + "-" + qdate[3:5] + "-" + qdate[0:2]
        return datetime.strptime(iso_date, '%Y-%m-%d')
