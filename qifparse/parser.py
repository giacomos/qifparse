# -*- coding: utf-8 -*-
import six
from datetime import datetime
from qifparse.qif import (
    Transaction,
    MemorizedTransaction,
    AmountSplit,
    Account,
    Investment,
    Category,
    Class,
    Qif,
)

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
        transactions_header = None
        parsers = {
            'category': cls_.parseCategory,
            'account': cls_.parseAccount,
            'transaction': cls_.parseTransaction,
            'investment': cls_.parseInvestment,
            'class': cls_.parseClass,
            'memorized': cls_.parseMemorizedTransaction
        }
        for chunk in chunks:
            if not chunk:
                continue
            first_line = chunk.split('\n')[0]
            if first_line == '!Type:Cat':
                last_type = 'category'
            elif first_line == '!Account':
                last_type = 'account'
            elif first_line in NON_INVST_ACCOUNT_TYPES:
                last_type = 'transaction'
                transactions_header = first_line
            elif first_line == '!Type:Invst':
                last_type = 'investment'
                transactions_header = first_line
            elif first_line == '!Type:Class':
                last_type = 'class'
            elif first_line == '!Type:Memorized':
                last_type = 'memorized'
                transactions_header = first_line
            elif chunk.startswith('!'):
                raise QifParserException('Header not reconized')
            # if no header is recognized then
            # we use the previous one
            item = parsers[last_type](chunk)
            if last_type == 'account':
                qif_obj.add_account(item)
                last_account = item
            elif last_type == 'transaction'\
                    or last_type == 'memorized' or last_type == 'investment':
                if last_account:
                    last_account.add_transaction(item,
                                                 header=transactions_header)
                else:
                    qif_obj.add_transaction(item,
                                            header=transactions_header)
            elif last_type == 'category':
                qif_obj.add_category(item)
            elif last_type == 'class':
                qif_obj.add_class(item)
        return qif_obj

    @classmethod
    def parseClass(cls_, chunk):
        """
        """
        curItem = Class()
        lines = chunk.split('\n')
        for line in lines:
            if not len(line) or line[0] == '\n' or \
                    line.startswith('!Type:Class'):
                continue
            elif line[0] == 'N':
                curItem.name = line[1:]
            elif line[0] == 'D':
                curItem.description = line[1:]
        return curItem

    @classmethod
    def parseCategory(cls_, chunk):
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
    def parseMemorizedTransaction(cls_, chunk, date_format=None):
        """
        """

        curItem = MemorizedTransaction()
        if date_format:
            curItem.date_format = date_format
        lines = chunk.split('\n')
        for line in lines:
            if not len(line) or line[0] == '\n' or \
                    line.startswith('!Type:Memorized'):
                continue
            elif line[0] == 'T':
                curItem.amount = float(line[1:])
            elif line[0] == 'C':
                curItem.cleared = line[1:]
            elif line[0] == 'P':
                curItem.payee = line[1:]
            elif line[0] == 'M':
                curItem.memo = line[1:]
            elif line[0] == 'K':
                curItem.mtype = line[1:]
            elif line[0] == 'A':
                if not curItem.address:
                    curItem.address = []
                curItem.address.append(line[1:])
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
            elif line[0] == 'A':
                split = curItem.splits[-1]
                if not split.address:
                    split.address = []
                split.address.append(line[1:])
            elif line[0] == '$':
                split = curItem.splits[-1]
                split.amount = float(line[1:-1])
            else:
                # don't recognise this line; ignore it
                print ("Skipping unknown line:\n" + str(line))
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
            elif line[0] == 'N':
                curItem.num = line[1:]
            elif line[0] == 'T':
                curItem.amount = float(line[1:])
            elif line[0] == 'C':
                curItem.cleared = line[1:]
            elif line[0] == 'P':
                curItem.payee = line[1:]
            elif line[0] == 'M':
                curItem.memo = line[1:]
            elif line[0] == '1':
                curItem.first_payment_date = line[1:]
            elif line[0] == '2':
                curItem.years_of_loan = line[1:]
            elif line[0] == '3':
                curItem.num_payments_done = line[1:]
            elif line[0] == '4':
                curItem.periods_per_year = line[1:]
            elif line[0] == '5':
                curItem.interests_rate = line[1:]
            elif line[0] == '6':
                curItem.current_loan_balance = line[1:]
            elif line[0] == '7':
                curItem.original_loan_amount = line[1:]
            elif line[0] == 'A':
                if not curItem.address:
                    curItem.address = []
                curItem.address.append(line[1:])
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
            elif line[0] == 'A':
                split = curItem.splits[-1]
                if not split.address:
                    split.address = []
                split.address.append(line[1:])
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
                curItem.quantity = float(line[1:])
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
