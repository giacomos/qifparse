# -*- coding: utf-8 -*-
import six
from datetime import datetime
from qifparse import DEFAULT_DATETIME_FORMAT

ACCOUNT_TYPES = [
    'Cash',
    'Bank',
    'CCard',
    'Oth A',
    'Oth L',
    'Invoice',  # Quicken for business only
    'Invst',
]

MEMORIZED_TRANSACTION_TYPES = [
    'C',  # Check
    'D',  # Deposit
    'P',  # Payment
    'I',  # Investment
    'E',  # Electronic payee
]


class Qif(object):
    def __init__(self):
        self._accounts = []
        self._categories = []
        self._classes = []
        self._transactions = {}
        self._last_header = None

    def add_account(self, item):
        if not isinstance(item, Account):
            raise RuntimeError(six.u("item not recognized"))
        self._accounts.append(item)

    def add_category(self, item):
        if not isinstance(item, Category):
            raise RuntimeError(six.u("item not recognized"))
        self._categories.append(item)

    def add_class(self, item):
        if not isinstance(item, Class):
            raise RuntimeError(six.u("item not recognized"))
        self._classes.append(item)

    def add_transaction(self, item, header=None):
        if not isinstance(item, Transaction)\
                and not isinstance(item, MemorizedTransaction):
            raise RuntimeError(six.u("item not recognized"))
        if header and not header in self._transactions:
            self._transactions[header] = []
        if not header:
            header = self._last_header
        else:
            self._last_header = header
        if not header:
            raise RuntimeError(six.u("no header provided yet"))
        self._transactions[header].append(item)

    def get_accounts(self, name=None, atype=None):
        if not name and not atype:
            return tuple(self._accounts)
        res = []
        for acc in self._accounts:
            valid_name = (not name or acc.name == name) and True or False
            valid_type = (not atype or acc.account_type == atype) \
                and True or False
            if valid_name and valid_type:
                res.append(acc)
        return tuple(res)

    def get_categories(self, name=None, income=None, expense=None):
        if income and expense:
            raise RuntimeError(
                six.u("item can be either income or expense, not both"))
        if not name and not income and not expense:
            return tuple(self._categories)
        res = []
        for cat in self._categories:
            valid_name = (not name or cat.name == name) and True or False
            valid_income = (not income or
                            cat.income == income) and True or False
            valid_expense = (not expense or
                             cat.expense == expense) and True or False
            if valid_name and valid_income and valid_expense:
                res.append(cat)
        return tuple(res)

    def get_classes(self, name=None):
        if not name:
            return tuple(self._classes)
        res = [klass for klass in self._classes if klass.name == name]
        return tuple(res)

    def get_transactions(self, recursive=False):
        if not recursive:
            return tuple(self._transactions.values())
        else:
            tr = []
            tr.extend(self._transactions.values)
            for acc in self._accounts:
                tr.extend(acc.transactions)

    def __str__(self):
        res = []
        if self._categories:
            res.append('!Type:Cat')
            for cat in self._categories:
                res.append(str(cat))
        for acc in self._accounts:
            res.append(str(acc))
        if self._classes:
            res.append('!Type:Class')
            for cat in self._classes:
                res.append(str(cat))
        if self._transactions:
            for header in self._transactions.keys():
                transactions = self._transactions[header]
                res.append(header)
                for tr in transactions:
                    res.append(str(tr))
        res.append('')
        return '\n'.join(res)


class Field(object):
    def __init__(self, name, ftype, first_letter, required=False,
                 default=None, custom_print_format=None):
        self.name = name
        self.ftype = ftype
        self.first_letter = first_letter
        self.required = required
        self.default = default
        self.custom_print_format = custom_print_format


class BaseEntry(object):

    _fields = []
    _sub_entry = False

    def __init__(self, **kwargs):
        self.date_format = DEFAULT_DATETIME_FORMAT
        for field in self._fields:
            val = kwargs.get(field.name, field.default)
            setattr(self, field.name, val)

    def __str__(self):
        res = []
        for field in self._fields:
            val = getattr(self, field.name)
            if not field.required and not val:
                continue
            elif field.required and not val:
                raise RuntimeError(
                    six.u("required field '%s' not yet set" % field.name))
            if field.custom_print_format:
                cformat = field.custom_print_format
                res.append(cformat % (field.first_letter, val))
            elif field.ftype == 'string':
                res.append('%s%s' % (field.first_letter, val))
            elif field.ftype == 'multilinestring':
                for line in val:
                    res.append('%s%s' % (field.first_letter, line))
            elif field.ftype == 'float':
                res.append('%s%.2f' % (field.first_letter, val))
            elif field.ftype == 'integer':
                res.append('%s%d' % (field.first_letter, val))
            elif field.ftype == 'datetime':
                sdate = val.strftime(self.date_format)
                res.append('%s%s' % (field.first_letter, sdate))
            elif field.ftype == 'reference':
                res.append('%s[%s]' % (field.first_letter, val))
            elif field.ftype == 'boolean':
                res.append('%s' % field.first_letter)
        if not self._sub_entry:
            res.append('^')
        return '\n'.join(res)


class Transaction(BaseEntry):
    _sub_entry = True
    _fields = [
        Field('date', 'datetime', 'D', required=True, default=datetime.now()),
        Field('num', 'string', 'N'),
        Field('amount', 'float', 'T', required=True),
        Field('cleared', 'string', 'C'),
        Field('payee', 'string', 'P'),
        Field('memo', 'string', 'M'),
        Field('address', 'multilinestring', 'A'),
        Field('category', 'string', 'L'),
        Field('reimbursable_expense', 'boolean', 'F'),
        Field('small_business_expense', 'boolean', 'X'),
        Field('to_account', 'reference', 'L'),
    ]

    def __init__(self, **kwargs):
        super(Transaction, self).__init__(**kwargs)
        self.splits = []

    def __str__(self):
        res = []
        fields = super(Transaction, self).__str__()
        res.append(fields)
        for split in self.splits:
            res.append(str(split))
        res.append('^')
        return '\n'.join(res)


class MemorizedTransaction(Transaction):
    _fields = [field for field in Transaction._fields
               if field.name not in ['date', 'num']]
    _fields.extend([
        Field('mtype', 'string', 'K'),
        Field('first_payment_date', 'datetime', '1'),
        Field('years_of_loan', 'string', '2'),
        Field('num_payments_done', 'string', '3'),
        Field('periods_per_year', 'string', '4'),
        Field('interests_rate', 'string', '5'),
        Field('current_loan_balance', 'string', '6'),
        Field('original_loan_amount', 'string', '7'),
    ])

    def set_mtype(self, type):
        if type and type not in MEMORIZED_TRANSACTION_TYPES:
            raise RuntimeError(
                six.u("%s is not a valid memorized transaction type" % type))
        self._mtype = type

    def get_mtype(self):
        return self._mtype

    mtype = property(get_mtype, set_mtype)


class AmountSplit(BaseEntry):
    _fields = [
        Field('category', 'string', 'S'),
        Field('to_account', 'reference', 'S'),
        Field('amount', 'float', '$'),
        Field('percent', 'string', '%'),
        Field('address', 'multilinestring', 'A'),
        Field('memo', 'string', 'M'),
    ]
    _sub_entry = True


class Investment(BaseEntry):
    _fields = [
        Field('date', 'datetime', 'D', required=True, default=datetime.now()),
        Field('action', 'string', 'N'),
        Field('security', 'string', 'Y'),
        Field('price', 'float', 'I', custom_print_format='%s%.3f'),
        Field('quantity', 'float', 'Q', custom_print_format='%s%.3f'),
        Field('cleared', 'string', 'C'),
        Field('amount', 'float', 'T'),
        Field('memo', 'string', 'M'),
        Field('first_line', 'string', 'P'),
        Field('to_account', 'reference', 'L'),
        Field('amount_transfer', 'float', '$'),
        Field('commission', 'float', 'O'),
    ]


class Account(BaseEntry):
    _fields = [
        Field('name', 'string', 'N', required=True),
        Field('description', 'string', 'D'),
        Field('account_type', 'string', 'T'),
        Field('credit_limit', 'float', 'L'),
        Field('balance_date', 'datetime', '/'),
        Field('balance_amount', 'float', '$')
    ]

    def __init__(self, **kwargs):
        super(Account, self).__init__(**kwargs)
        self._transactions = {}
        self._last_header = None

    def add_transaction(self, item, header=None):
        if not isinstance(item, Transaction) and \
           not isinstance(item, Investment):
            raise RuntimeError(
                six.u("item is not a Transaction or an Investment"))
        if header and not header in self._transactions:
            self._transactions[header] = []
        if not header:
            header = self._last_header
        else:
            self._last_header = header
        if not header:
            raise RuntimeError(six.u("no header provided yet"))
        self._transactions[header].append(item)

    def set_type(self, type):
        if type and type not in ACCOUNT_TYPES:
            raise RuntimeError(
                six.u("%s is not a valid account type" % type))
        self._type = type

    def get_type(self):
        return self._type

    account_type = property(get_type, set_type)

    def get_transactions(self):
        return tuple(self._transactions.values())

    def __str__(self):
        res = []
        res.append('!Account')
        fields = super(Account, self).__str__()
        res.append(fields)
        if self._transactions:
            for header in self._transactions.keys():
                transactions = self._transactions[header]
                res.append(header)
                for tr in transactions:
                    res.append(str(tr))
        return '\n'.join(res)


class Category(BaseEntry):
    _fields = [
        Field('name', 'string', 'N', required=True),
        Field('description', 'string', 'D'),
        Field('tax_related', 'boolean', 'T'),
        Field('expense', 'boolean', 'E', default=True),
        Field('income', 'boolean', 'I'),
        Field('budget_amount', 'float', 'B'),
        Field('tax_schedule_amount', 'string', 'R'),
    ]


class Class(BaseEntry):
    _fields = [
        Field('name', 'string', 'N', required=True),
        Field('description', 'string', 'D'),
    ]
