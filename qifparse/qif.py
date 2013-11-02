# -*- coding: utf-8 -*-
import six
from datetime import datetime
from qifparse import DEFAULT_DATETIME_FORMAT

ACCOUNT_TYPES = [
    'Cash',
    'Bank',
    'Ccard',
    'Oth A',
    'Oth L',
    'Invoice',  # Quicken for business only
    'Invst',
]


class Qif(object):
    def __init__(self):
        self._accounts = []
        self._categories = []

    def add(self, item):
        if not isinstance(item, Account) and \
           not isinstance(item, Category):
            raise RuntimeError(
                six.u("%s in not an Account or a Category"))
        elif isinstance(item, Account):
            self._accounts.append(item)
        else:
            self._categories.append(item)

    def get_account(self, name, default=None):
        for acc in self._accounts:
            if acc.name == name:
                return acc
        if not default:
            raise RuntimeError(
                six.u("account not found"))
        return None

    @property
    def accounts(self):
        return tuple(self._accounts)

    @property
    def categories(self):
        return tuple(self._categories)

    def __str__(self):
        res = []
        res.append('!Type:Cat')
        for cat in self._categories:
            res.append(str(cat))
        for acc in self._accounts:
            res.append(str(acc))
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

    def __init__(self, *args, **kwargs):
        self.date_format = DEFAULT_DATETIME_FORMAT
        for field in self._fields:
            setattr(self, field.name, field.default)

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
        Field('amount', 'float', 'T', required=True),
        Field('cleared', 'string', 'C'),
        Field('payee', 'string', 'P'),
        Field('memo', 'string', 'M'),
        Field('address', 'string', 'A'),
        Field('category', 'string', 'L'),
        Field('to_account', 'reference', 'L'),
    ]

    def __init__(self, *args, **kwargs):
        super(Transaction, self).__init__(*args, **kwargs)
        self.splits = []

    def __str__(self):
        res = []
        fields = super(Transaction, self).__str__()
        res.append(fields)
        for split in self.splits:
            res.append(str(split))
        res.append('^')
        return '\n'.join(res)


class AmountSplit(BaseEntry):
    _fields = [
        Field('category', 'string', 'S'),
        Field('to_account', 'reference', 'S'),
        Field('amount', 'float', '$', required=True),
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

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self._transactions = []

    def add(self, item):
        if not isinstance(item, Transaction) and \
           not isinstance(item, Investment):
            raise RuntimeError(
                six.u("item is not a Transaction or an Investment"))
        self._transactions.append(item)

    def set_type(self, type):
        if type and type not in ACCOUNT_TYPES:
            raise RuntimeError(
                six.u("%s is not a valid account type" % type))
        self._type = type

    def get_type(self):
        return self._type

    account_type = property(get_type, set_type)

    def __repr__(self):
        return '<Account: %s>' % self.name

    def __str__(self):
        res = []
        res.append('!Account')
        fields = super(Account, self).__str__()
        res.append(fields)
        if self._transactions:
            res.append('!Type:%s' % self.account_type)
            for tr in self._transactions:
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
