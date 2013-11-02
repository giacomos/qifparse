# -*- coding: utf-8 -*-
import six
from qifparse.account import Account
from qifparse.category import Category


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
