QIF Parser
============

.. image:: https://travis-ci.org/giacomos/qifparse.png?branch=master   
    :target: https://travis-ci.org/giacomos/qifparse

qifparse is a parser for Quicken interchange format files (.qif).


Usage
======

Here's a sample program::

   >>> from qifparse.parser import QifParser

   >>> qif = QifParser.parse(file('file.qif'))

   >>> qif.accounts
   (<Account: My Cash>, <Account: My Cc>)

   >>> qif.accounts[0].name
   'My Cash'

   >>> qif.categories
   [<Category: food>, <Category: food:lunch>]

   >>> qif.transactions
   {'My Cash': [<Transaction units=-6.5>, <Transaction units=-6.0>

   >>> str(qif)
   '!Type:Cat\nNfood\nE\n^\nNfood:lunch\nE\n^\n!Account\nNMy Cash\nTCash\n^\...
   ...


Test
======

  python setup.py test
